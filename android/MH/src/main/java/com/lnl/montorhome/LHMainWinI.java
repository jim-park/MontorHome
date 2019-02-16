package com.lnl.montorhome;

/**
 * Created by James Park
 * email: jim@linuxnetworks.co.uk
 * Date: 8/2/2559.
 */
public class LHMainWinI extends BaseShape {

    float lineCoords[] =  {
            -0.151748f, 0.164069f, 0.3f,
            -0.151748f, 0.026506f, 0.3f,
            -0.151746f, 0.02636f, 0.3f,
            -0.151724f, 0.025957f, 0.3f,
            -0.151659f, 0.025348f, 0.3f,
            -0.151529f, 0.024583f, 0.3f,
            -0.151311f, 0.023712f, 0.3f,
            -0.150982f, 0.022787f, 0.3f,
            -0.150520f, 0.021859f, 0.3f,
            -0.149901f, 0.020977f, 0.3f,
            -0.149104f, 0.020193f, 0.3f,
            -0.148105f, 0.019557f, 0.3f,
            -0.146881f, 0.019121f, 0.3f,
            -0.145411f, 0.018934f, 0.3f,
            -0.141222f, 0.018934f, 0.3f,
            -0.129386f, 0.018934f, 0.3f,
            -0.110994f, 0.018934f, 0.3f,
            -0.087140f, 0.018934f, 0.3f,
            -0.058915f, 0.018934f, 0.3f,
            -0.027412f, 0.018934f, 0.3f,
            0.006276f, 0.018934f, 0.3f,
            0.041057f, 0.018934f, 0.3f,
            0.075837f, 0.018934f, 0.3f,
            0.109525f, 0.018934f, 0.3f,
            0.141028f, 0.018934f, 0.3f,
            0.169253f, 0.018934f, 0.3f,
            0.171284f, 0.018996f, 0.3f,
            0.172947f, 0.019448f, 0.3f,
            0.174280f, 0.020216f, 0.3f,
            0.175318f, 0.021223f, 0.3f,
            0.176098f, 0.022394f, 0.3f,
            0.176656f, 0.023654f, 0.3f,
            0.177028f, 0.024927f, 0.3f,
            0.177251f, 0.026138f, 0.3f,
            0.177361f, 0.027212f, 0.3f,
            0.177395f, 0.028072f, 0.3f,
            0.177388f, 0.028643f, 0.3f,
            0.177378f, 0.028851f, 0.3f,
            0.177378f, 0.030619f, 0.3f,
            0.177378f, 0.035617f, 0.3f,
            0.177378f, 0.043384f, 0.3f,
            0.177378f, 0.053457f, 0.3f,
            0.177378f, 0.065375f, 0.3f,
            0.177378f, 0.078678f, 0.3f,
            0.177378f, 0.092904f, 0.3f,
            0.177378f, 0.10759f, 0.3f,
            0.177378f, 0.122277f, 0.3f,
            0.177378f, 0.136503f, 0.3f,
            0.177378f, 0.149805f, 0.3f,
            0.177378f, 0.161724f, 0.3f,
            0.177397f, 0.161898f, 0.3f,
            0.177424f, 0.162379f, 0.3f,
            0.177415f, 0.163105f, 0.3f,
            0.177326f, 0.164016f, 0.3f,
            0.177114f, 0.16505f, 0.3f,
            0.176734f, 0.166146f, 0.3f,
            0.176142f, 0.167242f, 0.3f,
            0.175295f, 0.168278f, 0.3f,
            0.174148f, 0.169191f, 0.3f,
            0.172658f, 0.16992f, 0.3f,
            0.170780f, 0.170405f, 0.3f,
            0.168471f, 0.170583f, 0.3f,
            0.164314f, 0.170591f, 0.3f,
            0.152566f, 0.170614f, 0.3f,
            0.134311f, 0.17065f, 0.3f,
            0.110634f, 0.170696f, 0.3f,
            0.082620f, 0.17075f, 0.3f,
            0.051352f, 0.170811f, 0.3f,
            0.017915f, 0.170876f, 0.3f,
            -0.016606f, 0.170943f, 0.3f,
            -0.051128f, 0.17101f, 0.3f,
            -0.084564f, 0.171075f, 0.3f,
            -0.115832f, 0.171136f, 0.3f,
            -0.143847f, 0.17119f, 0.3f,
            -0.145911f, 0.171082f, 0.3f,
            -0.147586f, 0.170715f, 0.3f,
            -0.148914f, 0.170141f, 0.3f,
            -0.149933f, 0.169411f, 0.3f,
            -0.150683f, 0.168576f, 0.3f,
            -0.151204f, 0.167686f, 0.3f,
            -0.151536f, 0.166794f, 0.3f,
            -0.151718f, 0.165949f, 0.3f,
            -0.151791f, 0.165203f, 0.3f,
            -0.151794f, 0.164607f, 0.3f,
            -0.151766f, 0.164212f, 0.3f,

    };

    short drawOrder[] = {   0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
                            11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
                            21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
                            31, 32, 33, 34, 35, 36, 37, 38, 39, 40,
                            41, 42, 43, 44, 45, 46, 47, 48, 49, 50,
                            51, 52, 53, 54, 55, 56, 57, 58, 59, 60,
                            61, 62, 63, 64, 65, 66, 67, 68, 69, 70,
                            71, 72, 73, 74, 75, 76, 77, 78, 79, 80,
                            81, 82, 83, 84,
                        };

    public LHMainWinI() {
        this.initVertexBuff(lineCoords);
        this.initListBuff(drawOrder);
    }
}
