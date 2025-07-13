# EmberBeard's Blender Toolbox

This is a small addon for blender containing a bunch of custom utilities to make my character/avatar development process for videogames a little easier. Maybe you'll find this useful.

## Tools


| Tool  | Description |
| ------------- |:-------------:|
| Recapture as shapekeys | This will scrub an animation timeline for markers. At each marker, for the selected mesh in the scene, it will save the animation pose of the mesh from the armature as a shapekey. It will then name that shape key to match the marker. This is especially useful for when you want to generate blendshapes off the shape of a face rig |
|Bind Control Rig|TO BE IMPLEMENTED<br>Given two armatures, this command will apply a copy transform constraint to each bone between the two armatures where the bone name matches. This way you can have a game ready rig that deforms a mesh and has minimal bloat, and a secondary armature with the same central bone structure and a whole host of control bones and constraints separately. Marrying the two together in one scene is now just a button press.|
|Remove Control Rig Bindings|This one is useful for when you need to iterate on your control rig and occasionally separate the two skeletons. Select your game rig and run this command - all copy transform constraints will be ripped off the skeleton.|