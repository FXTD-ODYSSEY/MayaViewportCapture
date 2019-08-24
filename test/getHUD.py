import os
import re

DIR = os.path.dirname(__file__)
path = os.path.join(DIR,"initHUD.mel")

with open(path, 'r') as f:
    HUD_list = re.findall(r"HUD.*?;", f.read())

print HUD_list
# NOTE 这是打印出来的数组
['HUDScripts.mel;', 'HUDObjDetBackfaces;', 'HUDObjDetSmoothness;', 'HUDObjDetInstance;', 'HUDObjDetDispLayer;', 'HUDObjDetDistFromCam;', 'HUDObjDetNumSelObjs;', 'HUDPolyCountVerts;', 'HUDPolyCountEdges;', 'HUDPolyCountFaces;', 'HUDPolyCountTriangles;', 'HUDPolyCountUVs;', 'HUDSubdLevel;', 'HUDSubdMode;', 'HUDParticleCount;', 'HUDCameraNames;',
'HUDViewportRenderer;', 'HUDSymmetry;', 'HUDCapsLock;', 'HUDFrameRate;', 'HUDGPUOverride;', 'HUDEMState;', 'HUDEvaluation;', 'HUDLoadingTextures;', 'HUDLoadingMaterials;', 'HUDCurrentFrame;', 'HUDIKSolverState;', 'HUDCurrentCharacter;', 'HUDPlaybackSpeed;', 'HUDHikKeyingMode;', 'HUDFbikKeyType;', 'HUDSoftSelectState;', 'HUDCurrentContainer;', 'HUDFocalLength;', 'HUDSceneTimecode;', 'HUDViewAxis;', 'HUDWalkMode;', 'HUDBlendShapeEdit;', 'HUD;', 'HUDActiveSculptMesh;', 'HUD3DCutSewUVActiveMesh;']

# NOTE 下面在 Maya 环境运行
from maya import cmds
for HUD in HUD_list:
    if not cmds.headsUpDisplay(HUD,ex=1):
        print HUD_list