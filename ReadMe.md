# EmberBeard's Blender Toolbox

This is a small addon for blender containing a bunch of custom utilities to make my character/avatar development process for videogames a little easier. Maybe you'll find this useful.

## Installation
1. Clone the repository
2. Right Click the folder called "EmberBeardToolbox" and compress it to a zip file
3. In blender goto Edit > Preferences > Add-ons
4. Click the little dropdown arrow in the top right and click "Install From Disk"
5. Select the zip file you made and accept
6. You're done - you should now have a tab called Ember's Tools in the right pain of the 3D viewport 😁

## Tools
| Tool  | Description |
| :------------- | :-------------|
| Recapture as shapekeys | This will scrub an animation timeline for markers. At each marker, for the selected mesh in the scene, it will save the animation pose of the mesh from the armature as a shapekey. It will then name that shape key to match the marker. This is especially useful for when you want to generate blendshapes off the shape of a face rig |
|Apply Shape Key Valeus To Mesh & Copy Shape Key Values To String|These two tools let you select a mesh and then instantly copy all shape keys with a non-zero value to your buffer as a string that can later be re-appled back to that mesh if you did something like reset your shapekey values.|
| Bind Control Rig | Given two armatures, this command will apply a copy transform constraint to each bone between the two armatures where the bone name matches. This way you can have a game ready rig that deforms a mesh and has minimal bloat, and a secondary armature with the same central bone structure and a whole host of control bones and constraints separately. Marrying the two together in one scene is now just a button press.|
| Remove Control Rig Bindings | This one is useful for when you need to iterate on your control rig and occasionally separate the two skeletons. Select your game rig and run this command - all copy transform constraints will be ripped off the skeleton. |
| Import Animation Markers | This will allow you to provide your own .txt file and will import all the names to a marker on a per line basis - which is to say 1 line of the .txt file equals 1 marker in the animation timeline. The line number minus 1 equals where that marker will sit in the timeline. |

## Extra resources & info
For the Animation Markers importer tool a default ans simple "BasicMarkers.txt" is provided which has all Vismese, a short set of useful shapes for VRChat as a minimal basis, all unified expressions and a subset of the MMD shapes. You can read more about what these shapes are and what they look like here:

- **Visemes**:https://developers.meta.com/horizon/documentation/unity/audio-ovrlipsync-viseme-reference/
- **Visemes - reference/example**: https://www.furaffinity.net/view/40994250/ 
- **VRCFT Unified Expressions**: https://docs.vrcft.io/docs/tutorial-avatars/tutorial-avatars-extras/unified-blendshapes
- **MMD blend shapes**: https://www.deviantart.com/xoriu/art/MMD-Facial-Expressions-Chart-341504917

## AI Disclaimer
I hate generative AI and I don't like posers that pretend to be good at something they're not. Vibe coders and AI artists suck in equal measure in my eye. It is, therefore, important for me at least to discuss how I used Generative AI for this project. My background is in computer science and I did lots of C/C++/C# programming (even dabbled in a little assembly). Strict types and stricter rules that tell you exactly where and why I fucked up is how I like to develop software. Python, therefore, is one of the worst languages I've had the misfortune of working with (in my personal oppinion, second only to javascript). As such, I did not vibe code, I did genuinely make a sincere effort to try and learn python myself with only meager success. Eventually I did reach out for AI to help, but not in the vibe coding "please make this thing and have no errors" sort of way. I asked the AI to give me examples, references and if I got really stuck, I gave it the code I wrote and asked it to explain what was wrong to me. As someone with slight reading issues as well, subtle and regular typos in a loosely typed language was a nightmare for me to debug. So no, this project wouldn't have been possible without generative AI for me, but equally no, this was not vibe coded. I treated the AI like a colleague I was consulting with and I will say with hand on heart, I do in fact own every line of code in this code base and if anything breaks I will take responsibility for it.

Additionally:
1. I also only used free AI solutions so the tech oligarchs don't get any credit either.

2. I cannot say with certainty that any code I got wasn't from copy-left software licenses so I'm releasing this back into the wild as open and free for everyone.