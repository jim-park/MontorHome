package com.opengl_test.jim.opengl_test;

/**
 * Created by jim on 8/2/2559.
 */
public class LHStoreCatch extends BaseShape {

    float lineCoords[] =  {
            -0.112179f, -0.206427f, 0.3f,
            -0.101140f, -0.206427f, 0.3f,
            -0.100779f, -0.206477f, 0.3f,
            -0.100479f, -0.206617f, 0.3f,
            -0.100232f, -0.206828f, 0.3f,
            -0.100035f, -0.207093f, 0.3f,
            -0.099882f, -0.207393f, 0.3f,
            -0.099766f, -0.207711f, 0.3f,
            -0.099683f, -0.20803f, 0.3f,
            -0.099628f, -0.20833f, 0.3f,
            -0.099594f, -0.208594f, 0.3f,
            -0.099577f, -0.208806f, 0.3f,
            -0.099571f, -0.208945f, 0.3f,
            -0.099570f, -0.208996f, 0.3f,
            -0.099570f, -0.214126f, 0.3f,
            -0.099601f, -0.214716f, 0.3f,
            -0.099686f, -0.215208f, 0.3f,
            -0.099815f, -0.215611f, 0.3f,
            -0.099977f, -0.215934f, 0.3f,
            -0.100161f, -0.216185f, 0.3f,
            -0.100355f, -0.216374f, 0.3f,
            -0.100549f, -0.216509f, 0.3f,
            -0.100733f, -0.2166f, 0.3f,
            -0.100895f, -0.216655f, 0.3f,
            -0.101024f, -0.216683f, 0.3f,
            -0.101109f, -0.216693f, 0.3f,
            -0.101140f, -0.216695f, 0.3f,
            -0.112179f, -0.216695f, 0.3f,
            -0.112539f, -0.216644f, 0.3f,
            -0.112840f, -0.216504f, 0.3f,
            -0.113086f, -0.216293f, 0.3f,
            -0.113284f, -0.216029f, 0.3f,
            -0.113437f, -0.215728f, 0.3f,
            -0.113553f, -0.21541f, 0.3f,
            -0.113635f, -0.215092f, 0.3f,
            -0.113691f, -0.214792f, 0.3f,
            -0.113724f, -0.214527f, 0.3f,
            -0.113742f, -0.214316f, 0.3f,
            -0.113748f, -0.214176f, 0.3f,
            -0.113749f, -0.214126f, 0.3f,
            -0.113749f, -0.208996f, 0.3f,
            -0.113718f, -0.208406f, 0.3f,
            -0.113633f, -0.207914f, 0.3f,
            -0.113503f, -0.207511f, 0.3f,
            -0.113342f, -0.207188f, 0.3f,
            -0.113158f, -0.206937f, 0.3f,
            -0.112964f, -0.206748f, 0.3f,
            -0.112769f, -0.206613f, 0.3f,
            -0.112586f, -0.206522f, 0.3f,
            -0.112424f, -0.206467f, 0.3f,
            -0.112295f, -0.206439f, 0.3f,
            -0.112209f, -0.206428f, 0.3f,
    };

    short drawOrder[] = {   0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
                            11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
                            21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
                            31, 32, 33, 34, 35, 36, 37, 38, 39, 40,
                            41, 42, 43, 44, 45, 46, 47, 48, 49, 50,
                            51,
                        };


    public LHStoreCatch(){
        this.initVertexBuff(lineCoords);
        this.initListBuff(drawOrder);
    }
}
