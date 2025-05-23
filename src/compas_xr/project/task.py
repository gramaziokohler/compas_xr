from compas.datastructures import Mesh
from compas.geometry import Frame, Transformation
from compas.data import Data

class Action(Data):

    """An action to be performed in the XR environment."""

    def __init__(self, name, mesh, start_frame, target_frame, motion_frames, description=None):
        super(Action, self).__init__()
        self.name = name
        self.mesh = mesh
        self.start_frame = start_frame
        self.target_frame = target_frame
        self.motion_frames = motion_frames
        self.target_motion_frames = self._create_action_frames(start_frame, target_frame, motion_frames)
        self.action_meshes = self._create_action_meshes(mesh, start_frame, self.target_motion_frames)
        self.description = description

    @property
    def __data__(self):
        return {
            "name": self.name,
            "mesh": self.mesh.__data__,
            "start_frame": self.start_frame.__data__,
            "target_frame": self.target_frame.__data__,
            "motion_frames": [frame.__data__ for frame in self.motion_frames],
            "description": self.description,
        }

    @classmethod
    def __from_data__(cls, data):
        return cls(
            name=data["name"],
            mesh=Mesh.__from_data__(data["mesh"]),
            start_frame=Frame.__from_data__(data["start_frame"]),
            target_frame=Frame.__from_data__(data["target_frame"]),
            motion_frames=[Frame.__from_data__(frame) for frame in data["motion_frames"]],
            description=data.get("description"),
        )
    
    def _create_action_frames(self, start_frame, target_frame, motion_frames):
        """Create action frames based on the given start and target frames."""
        target_motion_frames = []
        transformation = Transformation.from_frame_to_frame(start_frame, target_frame)
        for frame in motion_frames:
            transformed_frame = frame.transformed(transformation)
            target_motion_frames.append(transformed_frame)
        return target_motion_frames
    
    def _create_action_meshes(self, mesh, start_frame, target_motion_frames):
        """Create action meshes based on the given mesh and frames."""
        action_meshes = []
        for frame in target_motion_frames:
            transformation = Transformation.from_frame_to_frame(start_frame, frame)
            transformed_mesh = mesh.transformed(transformation)
            action_meshes.append(transformed_mesh)
        return action_meshes
    

class Task(Data):

    """A task to be performed in the XR environment."""

    def __init__(self, name, actions, description=None):
        super(Task, self).__init__()
        self.name = name
        self.actions = actions
        self.description = description

    @property
    def __data__(self):
        return {
            "name": self.name,
            "actions": [action.__data__ for action in self.actions],
            "description": self.description,
        }
    
    @classmethod
    def __from_data__(cls, data):
        return cls(
            name=data["name"],
            actions=[Action.__from_data__(action) for action in data["actions"]],
            description=data.get("description"),
        )