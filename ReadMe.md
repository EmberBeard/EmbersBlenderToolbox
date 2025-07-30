# EmberBeard's Blender Toolbox

This is a small addon for blender containing a bunch of custom utilities to make my character/avatar development process for videogames a little easier. Maybe you'll find this useful.

## Tools


| Tool  | Description |
| :------------- | :-------------|
| Recapture as shapekeys | This will scrub an animation timeline for markers. At each marker, for the selected mesh in the scene, it will save the animation pose of the mesh from the armature as a shapekey. It will then name that shape key to match the marker. This is especially useful for when you want to generate blendshapes off the shape of a face rig |
| Bind Control Rig | Given two armatures, this command will apply a copy transform constraint to each bone between the two armatures where the bone name matches. This way you can have a game ready rig that deforms a mesh and has minimal bloat, and a secondary armature with the same central bone structure and a whole host of control bones and constraints separately. Marrying the two together in one scene is now just a button press.|
| Remove Control Rig Bindings | This one is useful for when you need to iterate on your control rig and occasionally separate the two skeletons. Select your game rig and run this command - all copy transform constraints will be ripped off the skeleton. |
| Import Animation Markers | This will allow you to provide your own .txt file and will import all the names to a marker on a per line basis - which is to say 1 line of the .txt file equals 1 marker in the animation timeline. The line number minus 1 equals where that marker will sit in the timeline. |

## Extra resources & info
For the Animation Markers importer tool a default ans simple "BasicMarkers.txt" is provided which has all Vismese, a short set of useful shapes for VRChat as a minimal basis, all unified expressions and a subset of the MMD shapes. You can read more about what these shapes are and what they look like here:

- **Visemes**:https://developers.meta.com/horizon/documentation/unity/audio-ovrlipsync-viseme-reference/
- **Visemes - reference/example**: https://www.furaffinity.net/view/40994250/ 
- **VRCFT Unified Expressions**: https://docs.vrcft.io/docs/tutorial-avatars/tutorial-avatars-extras/unified-blendshapes
- **MMD blend shapes**: https://www.deviantart.com/xoriu/art/MMD-Facial-Expressions-Chart-341504917