package com.opengl_test.jim.opengl_test;

/**
 * Created by jim on 8/2/2559.
 */
public class LHMainWinO extends BaseShape {

    float lineCoords[] =  {
            -0.159978f, 0.173142f, 0.3f,
            -0.159978f, 0.020205f, 0.3f,
            -0.159976f, 0.020043f, 0.3f,
            -0.159953f, 0.019596f, 0.3f,
            -0.159885f, 0.018918f, 0.3f,
            -0.159748f, 0.018067f, 0.3f,
            -0.159519f, 0.017099f, 0.3f,
            -0.159174f, 0.016071f, 0.3f,
            -0.158688f, 0.015039f, 0.3f,
            -0.158039f, 0.014058f, 0.3f,
            -0.157202f, 0.013187f, 0.3f,
            -0.156153f, 0.01248f, 0.3f,
            -0.154868f, 0.011995f, 0.3f,
            -0.153324f, 0.011787f, 0.3f,
            -0.148926f, 0.011787f, 0.3f,
            -0.136498f, 0.011787f, 0.3f,
            -0.117186f, 0.011787f, 0.3f,
            -0.092138f, 0.011787f, 0.3f,
            -0.062502f, 0.011787f, 0.3f,
            -0.029424f, 0.011787f, 0.3f,
            0.005949f, 0.011787f, 0.3f,
            0.042469f, 0.011787f, 0.3f,
            0.078989f, 0.011787f, 0.3f,
            0.114362f, 0.011787f, 0.3f,
            0.147440f, 0.011787f, 0.3f,
            0.177077f, 0.011787f, 0.3f,
            0.179209f, 0.011856f, 0.3f,
            0.180956f, 0.012359f, 0.3f,
            0.182355f, 0.013212f, 0.3f,
            0.183445f, 0.014332f, 0.3f,
            0.184264f, 0.015634f, 0.3f,
            0.184849f, 0.017035f, 0.3f,
            0.185240f, 0.01845f, 0.3f,
            0.185474f, 0.019797f, 0.3f,
            0.185590f, 0.02099f, 0.3f,
            0.185626f, 0.021946f, 0.3f,
            0.185619f, 0.022582f, 0.3f,
            0.185608f, 0.022812f, 0.3f,
            0.185608f, 0.024778f, 0.3f,
            0.185608f, 0.030335f, 0.3f,
            0.185608f, 0.038969f, 0.3f,
            0.185608f, 0.050168f, 0.3f,
            0.185608f, 0.063419f, 0.3f,
            0.185608f, 0.078208f, 0.3f,
            0.185608f, 0.094024f, 0.3f,
            0.185608f, 0.110352f, 0.3f,
            0.185608f, 0.12668f, 0.3f,
            0.185608f, 0.142495f, 0.3f,
            0.185608f, 0.157285f, 0.3f,
            0.185608f, 0.170535f, 0.3f,
            0.185628f, 0.170729f, 0.3f,
            0.185656f, 0.171263f, 0.3f,
            0.185647f, 0.172071f, 0.3f,
            0.185554f, 0.173084f, 0.3f,
            0.185331f, 0.174234f, 0.3f,
            0.184932f, 0.175452f, 0.3f,
            0.184311f, 0.176671f, 0.3f,
            0.183421f, 0.177822f, 0.3f,
            0.182217f, 0.178837f, 0.3f,
            0.180652f, 0.179648f, 0.3f,
            0.178680f, 0.180186f, 0.3f,
            0.176256f, 0.180385f, 0.3f,
            0.171891f, 0.180394f, 0.3f,
            0.159555f, 0.180419f, 0.3f,
            0.140387f, 0.180459f, 0.3f,
            0.115526f, 0.18051f, 0.3f,
            0.086111f, 0.18057f, 0.3f,
            0.053279f, 0.180638f, 0.3f,
            0.018170f, 0.18071f, 0.3f,
            -0.018078f, 0.180785f, 0.3f,
            -0.054325f, 0.180859f, 0.3f,
            -0.089434f, 0.180931f, 0.3f,
            -0.122266f, 0.180999f, 0.3f,
            -0.151682f, 0.18106f, 0.3f,
            -0.153849f, 0.180939f, 0.3f,
            -0.155608f, 0.180532f, 0.3f,
            -0.157002f, 0.179894f, 0.3f,
            -0.158072f, 0.179082f, 0.3f,
            -0.158859f, 0.178153f, 0.3f,
            -0.159407f, 0.177164f, 0.3f,
            -0.159755f, 0.176172f, 0.3f,
            -0.159947f, 0.175233f, 0.3f,
            -0.160023f, 0.174403f, 0.3f,
            -0.160026f, 0.173741f, 0.3f,
            -0.159997f, 0.173301f, 0.3f,

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

    float color[] = { 1, 0, 0, 1.0f };  // Set the colour with red, green blue and alpha (opacity) values


    public LHMainWinO(){
        this.initVertexBuff(lineCoords);
        this.initListBuff(drawOrder);
        this.initColor(color);
    }
}
