********************************************************************************
API Reference
********************************************************************************
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
COMPAS XR - Python Library for CAD Functionalities
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. toctree::
    :maxdepth: 1

    api/compas_xr

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
COMPAS XR Unity - Application & Unity File
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

""""""""""""""""
Initialize.unity
""""""""""""""""

- **FirebaseInitializer.cs** (initializes Firebase with configured settings and manages scene transitions upon successful initialization, utilizing MqttFirebaseConfigManager for disconnecting MQTT and HelpersExtensions.ChangeScene for scene navigation.)
- **FirebaseConfigSettings.cs** (manages user input Firebase configuration settings, saving and loading them from Player Preferences, and updates a singleton instance FirebaseManager with these values.)
- **MqttFirebaseConfigManager.cs** (manages MQTT connections, handles message events, and allows subscription to custom topics for sending Firebase configuration information.)
- **LogManager.cs** (manages logging by creating a log directory, deleting old log files, and writing log messages with timestamps, scene names, log types, and stack traces to a specified log file.)

"""""""""""
Login.unity
"""""""""""

- **UserManager.cs** (manages user records and device configurations in Firebase, allowing creation of new users and updating existing ones based on unique identifiers.)


""""""""""""""
MainGame.unity
""""""""""""""

- **AppModeControler.cs** (defines a ModeControler class within the CompasXR.AppSettings namespace that manages two enums, VisulizationMode and TouchMode, to control visualization modes and touch interaction modes in an application.)
- **ApplicationSettings.cs** (defines a ApplicationSettings class within the CompasXR.AppSettings namespace, which includes properties for managing the project name, storage folder path, and a boolean for z-to-y axis remapping configuration in an application.)
- **CheckFirebase.cs** (defines a CheckFirebase class within the CompasXR.Database.FirebaseManagement namespace, which checks and initializes Firebase on the Start method, and triggers an event to confirm successful initialization or logs an error if it fails.)
- **CoreData.cs** (defines several classes within the CompasXR.Core.Data namespace, handling data structures, data conversion, and deserialization. The classes represent parts of a building assembly, including nodes, parts, frames, attributes, building plans, steps, data, and user information.)
- **DatabaseManager.cs** (manages a Unity application's integration with Firebase Realtime Database and Storage, handling data synchronization, event-driven updates, and deserialization of complex data structures for a construction planning and tracking system.)
- **Eventmanager.cs** (orchestrates the setup, initialization, and event-driven interactions between various components and Firebase services within the CompasXR Unity application.)
- **Extentions.cs** (extends Unity engine functionality with methods for scene management, object finding, value remapping, UI interaction checks, data type printing, camera-facing behavior, and object position storage in the CompasXR.Core.Extentions namespace.)
- **FirebaseManager.cs** (implements a sealed singleton class using the Singleton Pattern to manage Firebase configuration settings such as appId, apiKey, databaseUrl, storageBucket, and projectId, with initialization based on the current operating system detected by OperatingSystemManager.GetCurrentOS().)
- **InstantiateObjects.cs** (manages the AR space instantiation and control of objects based on building plan data, handling object visualization, user indicators, and interaction with materials and textures.)
- **MQTTDataCompasXR.cs** (define classes and data structures for managing MQTT communication, service states, and custom message formats within the Compas XR system, ensuring standardized messaging and service management across robotic applications.)
- **MqttTrajectoryManager.cs** (implements an MQTT client in Unity for managing robot trajectory requests and approvals, featuring message handling, connection management, and UI interactions.)
- **ObjectTransformations.cs** ( provides static methods for converting object positions and rotations between Unity and Rhino coordinate systems, utilizing various rotation and transformation algorithms.)
- **OperatingSystemManager.cs** (identifies and logs the current operating system (Android, iOS, or Unknown) based on the Unity platform, providing a static method to retrieve this information.)
- **QRLocalization.cs** (manages the real-time localization of objects in a scene based on QR code data, updating their positions and rotations dynamically.)
- **RosConnectionManager.cs** ( handles the connection to a ROSBridge server, manages connection status, and updates UI elements based on communication toggle state in the CompasXR Application.)
- **ScrollSearchManager.cs** (manages scrollable UI functionality for searching and interacting with elements, including dynamic cell creation, scrolling control, and object coloring based on user selection in the CompasXR Application.)
- **TrajectoryVisualizer.cs** (namespace manages robot visualization and interaction in Unity, facilitating tasks such as setting up robots in the scene, instantiating trajectories, configuring robot configurations from dictionaries, and attaching elements to end effectors based on received data.)
- **UIFunctionalities.cs** (manages various UI elements and functionalities, including primary UI controls, visualizer menus, additional menu functionalities, and communication settings such as MQTT and ROS connections.)


