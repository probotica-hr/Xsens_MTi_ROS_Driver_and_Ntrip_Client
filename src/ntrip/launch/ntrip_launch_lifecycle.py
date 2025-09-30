from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, RegisterEventHandler, EmitEvent
from launch.substitutions import LaunchConfiguration
from ament_index_python.packages import get_package_share_directory
import os

from launch_ros.event_handlers import OnStateTransition
from launch_ros.events.lifecycle import ChangeState
from lifecycle_msgs.msg import Transition
from launch_ros.actions import LifecycleNode


def generate_launch_description():
    # Declare the log level argument
    log_level_arg = DeclareLaunchArgument(
        'log_level',
        default_value='info',
        description='Logging level (debug, info, warn, error, fatal)',
        choices=['debug', 'info', 'warn', 'error', 'fatal']
    )

    namespace_arg = DeclareLaunchArgument(
        'namespace',
        default_value='marinero',  # Change this to your preferred default namespace
        description='Namespace for the ntrip_client'
    )

    ntrip_config_arg = DeclareLaunchArgument(
        'ntrip_config',
        default_value=os.path.join(
                get_package_share_directory('ntrip'),
                'config',
                'ntrip_config.yaml'
            ),
        description='NTRIP configuration'
        )

    # Create the node configuration
    ntrip_lifecycle_node = LifecycleNode(
        package='ntrip',
        executable='ntrip_lifecycle',
        name='ntrip_client_lifecycle',
        namespace=LaunchConfiguration('namespace'),
        output='screen',
        parameters=[LaunchConfiguration('ntrip_config')],
        # Topic Remapping
        remappings=[
            ('/nmea', [LaunchConfiguration('namespace'), '/nmea']),
            ('/rtcm', [LaunchConfiguration('namespace'), '/rtcm']),
        ],
        # Add arguments for log level
        arguments=['--ros-args', '--log-level', LaunchConfiguration('log_level')]
    )

    # When the node reaches "unconfigured", send CONFIGURE
    configure_event_handler = RegisterEventHandler(
        OnStateTransition(
            target_lifecycle_node=ntrip_lifecycle_node,
            goal_state='configuring',
            entities=[
                EmitEvent(
                    event = ChangeState(
                        lifecycle_node_matcher=ntrip_lifecycle_node,
                        transition_id=Transition.TRANSITION_CONFIGURE
                    )
                )
            ]
        )
    )

    # When the node reaches "inactive", send ACTIVATE
    activate_event_handler = RegisterEventHandler(
        OnStateTransition(
            target_lifecycle_node=ntrip_lifecycle_node,
            goal_state='activating',
            entities=[
                EmitEvent(
                    event = ChangeState(
                        lifecycle_node_matcher=ntrip_lifecycle_node,
                        transition_id=Transition.TRANSITION_ACTIVATE
                    )
                )
            ]
        )
    )

    return LaunchDescription([
        log_level_arg,  # Include the log level argument
        namespace_arg,
        ntrip_config_arg,
        configure_event_handler,
        activate_event_handler,
        ntrip_lifecycle_node,   # Include the node configuration
    ])
