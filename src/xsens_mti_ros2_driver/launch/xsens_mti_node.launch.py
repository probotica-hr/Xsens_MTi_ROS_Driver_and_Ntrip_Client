from launch import LaunchDescription
from launch.actions import SetEnvironmentVariable, DeclareLaunchArgument, GroupAction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node, PushRosNamespace
from ament_index_python.packages import get_package_share_directory
from pathlib import Path

def generate_launch_description():

    ld = LaunchDescription()

    ld.add_action(SetEnvironmentVariable('RCUTILS_LOGGING_USE_STDOUT', '1'))
    ld.add_action(SetEnvironmentVariable('RCUTILS_LOGGING_BUFFERED_STREAM', '1'))

    namespace_arg = DeclareLaunchArgument(
        'namespace',
        default_value='xsens',
        description='ROS namespace for the xsens node'
    )
    ld.add_action(namespace_arg)

    parameters_file_path = Path(get_package_share_directory('xsens_mti_ros2_driver'), 'param', 'xsens_mti_node.yaml')
    xsens_mti_node = Node(
            package='xsens_mti_ros2_driver',
            executable='xsens_mti_node',
            name='xsens_mti_node',
            output='screen',
            parameters=[parameters_file_path],
            arguments=[]
            )

    namespaced_group = GroupAction(
        actions=[
            PushRosNamespace(LaunchConfiguration('namespace')),
            xsens_mti_node,
        ]
    )
    ld.add_action(namespaced_group)

    return ld
