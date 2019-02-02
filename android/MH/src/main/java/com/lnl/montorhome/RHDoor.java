package com.lnl.montorhome;

/**
 * Created by jim on 8/2/2559.
 */
public class RHDoor extends BaseShape {

    float lineCoords[] =  {
            -0.271808f, -0.281795f, -0.25f,
            -0.271808f, 0.127469f, -0.25f,
            -0.432162f, 0.127469f, -0.25f,
            -0.517817f, -0.020902f, -0.25f,
            -0.517817f, -0.176243f, -0.25f,
            -0.515797f, -0.176202f, -0.25f,
            -0.513862f, -0.176162f, -0.25f,
            -0.512002f, -0.176131f, -0.25f,
            -0.510207f, -0.176116f, -0.25f,
            -0.508465f, -0.176125f, -0.25f,
            -0.506767f, -0.176165f, -0.25f,
            -0.505101f, -0.176244f, -0.25f,
            -0.503458f, -0.176368f, -0.25f,
            -0.501826f, -0.176546f, -0.25f,
            -0.500196f, -0.176785f, -0.25f,
            -0.498556f, -0.177092f, -0.25f,
            -0.496897f, -0.177476f, -0.25f,
            -0.494852f, -0.177996f, -0.25f,
            -0.492636f, -0.178579f, -0.25f,
            -0.490284f, -0.179233f, -0.25f,
            -0.487834f, -0.179969f, -0.25f,
            -0.485320f, -0.180797f, -0.25f,
            -0.482778f, -0.181726f, -0.25f,
            -0.480245f, -0.182767f, -0.25f,
            -0.477757f, -0.18393f, -0.25f,
            -0.475350f, -0.185225f, -0.25f,
            -0.473059f, -0.186661f, -0.25f,
            -0.470920f, -0.188248f, -0.25f,
            -0.468971f, -0.189998f, -0.25f,
            -0.468824f, -0.190143f, -0.25f,
            -0.468410f, -0.190555f, -0.25f,
            -0.467767f, -0.191194f, -0.25f,
            -0.466933f, -0.192024f, -0.25f,
            -0.465947f, -0.193005f, -0.25f,
            -0.464845f, -0.194101f, -0.25f,
            -0.463668f, -0.195272f, -0.25f,
            -0.462452f, -0.196482f, -0.25f,
            -0.461236f, -0.197691f, -0.25f,
            -0.460058f, -0.198862f, -0.25f,
            -0.458957f, -0.199958f, -0.25f,
            -0.457970f, -0.200939f, -0.25f,
            -0.451634f, -0.210465f, -0.25f,
            -0.446219f, -0.220126f, -0.25f,
            -0.441653f, -0.22974f, -0.25f,
            -0.437866f, -0.239122f, -0.25f,
            -0.434787f, -0.248089f, -0.25f,
            -0.432348f, -0.256457f, -0.25f,
            -0.430476f, -0.264042f, -0.25f,
            -0.429103f, -0.27066f, -0.25f,
            -0.428157f, -0.276127f, -0.25f,
            -0.427568f, -0.28026f, -0.25f,
            -0.427267f, -0.282874f, -0.25f,
            -0.427182f, -0.283787f, -0.25f,
            -0.425114f, -0.28376f, -0.25f,
            -0.419269f, -0.283685f, -0.25f,
            -0.410188f, -0.283569f, -0.25f,
            -0.398409f, -0.283418f, -0.25f,
            -0.384472f, -0.283239f, -0.25f,
            -0.368917f, -0.28304f, -0.25f,
            -0.352282f, -0.282827f, -0.25f,
            -0.335108f, -0.282606f, -0.25f,
            -0.317934f, -0.282386f, -0.25f,
            -0.301300f, -0.282173f, -0.25f,
            -0.285745f, -0.281974f, -0.25f,
    };

    short drawOrder[] = {   0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
                            11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
                            21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
                            31, 32, 33, 34, 35, 36, 37, 38, 39, 40,
                            41, 42, 43, 44, 45, 46, 47, 48, 49, 50,
                            51, 52, 53, 54, 55, 56, 57, 58, 59, 60,
                            61, 62, 63
                        };


    public RHDoor(){
        this.initVertexBuff(lineCoords);
        this.initListBuff(drawOrder);
    }
}
