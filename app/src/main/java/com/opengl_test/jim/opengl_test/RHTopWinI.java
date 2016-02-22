package com.opengl_test.jim.opengl_test;

/**
 * Created by jim on 8/2/2559.
 */
public class RHTopWinI extends BaseShape {

    float lineCoords[] =  {
            -0.446978f, 0.33349f, -0.3f,
            -0.291692f, 0.33349f, -0.3f,
            -0.291627f, 0.333488f, -0.3f,
            -0.291448f, 0.333477f, -0.3f,
            -0.291177f, 0.333445f, -0.3f,
            -0.290838f, 0.333383f, -0.3f,
            -0.290452f, 0.33328f, -0.3f,
            -0.290044f, 0.333126f, -0.3f,
            -0.289636f, 0.332911f, -0.3f,
            -0.289250f, 0.332624f, -0.3f,
            -0.288911f, 0.332254f, -0.3f,
            -0.288640f, 0.331792f, -0.3f,
            -0.288461f, 0.331228f, -0.3f,
            -0.288396f, 0.33055f, -0.3f,
            -0.288396f, 0.329637f, -0.3f,
            -0.288396f, 0.327057f, -0.3f,
            -0.288396f, 0.323048f, -0.3f,
            -0.288396f, 0.317848f, -0.3f,
            -0.288396f, 0.311695f, -0.3f,
            -0.288396f, 0.304828f, -0.3f,
            -0.288396f, 0.297484f, -0.3f,
            -0.288396f, 0.289903f, -0.3f,
            -0.288396f, 0.282321f, -0.3f,
            -0.288396f, 0.274977f, -0.3f,
            -0.288396f, 0.26811f, -0.3f,
            -0.288396f, 0.261958f, -0.3f,
            -0.288403f, 0.261887f, -0.3f,
            -0.288432f, 0.261691f, -0.3f,
            -0.288496f, 0.261396f, -0.3f,
            -0.288608f, 0.261026f, -0.3f,
            -0.288781f, 0.260606f, -0.3f,
            -0.289028f, 0.260161f, -0.3f,
            -0.289362f, 0.259716f, -0.3f,
            -0.289796f, 0.259296f, -0.3f,
            -0.290343f, 0.258926f, -0.3f,
            -0.291016f, 0.258631f, -0.3f,
            -0.291827f, 0.258435f, -0.3f,
            -0.292791f, 0.258365f, -0.3f,
            -0.294843f, 0.258365f, -0.3f,
            -0.300643f, 0.258365f, -0.3f,
            -0.309655f, 0.258365f, -0.3f,
            -0.321344f, 0.258365f, -0.3f,
            -0.335174f, 0.258365f, -0.3f,
            -0.350611f, 0.258365f, -0.3f,
            -0.367118f, 0.258365f, -0.3f,
            -0.384161f, 0.258365f, -0.3f,
            -0.401204f, 0.258365f, -0.3f,
            -0.417711f, 0.258365f, -0.3f,
            -0.433148f, 0.258365f, -0.3f,
            -0.446978f, 0.258365f, -0.3f,
            -0.447038f, 0.258374f, -0.3f,
            -0.447204f, 0.25841f, -0.3f,
            -0.447457f, 0.258483f, -0.3f,
            -0.447775f, 0.258605f, -0.3f,
            -0.448139f, 0.258785f, -0.3f,
            -0.448529f, 0.259035f, -0.3f,
            -0.448924f, 0.259366f, -0.3f,
            -0.449304f, 0.259789f, -0.3f,
            -0.449650f, 0.260314f, -0.3f,
            -0.449940f, 0.260952f, -0.3f,
            -0.450155f, 0.261714f, -0.3f,
            -0.450274f, 0.262611f, -0.3f,
            -0.450274f, 0.263515f, -0.3f,
            -0.450274f, 0.266071f, -0.3f,
            -0.450274f, 0.270042f, -0.3f,
            -0.450274f, 0.275192f, -0.3f,
            -0.450274f, 0.281286f, -0.3f,
            -0.450274f, 0.288088f, -0.3f,
            -0.450274f, 0.295361f, -0.3f,
            -0.450274f, 0.302871f, -0.3f,
            -0.450274f, 0.31038f, -0.3f,
            -0.450274f, 0.317654f, -0.3f,
            -0.450274f, 0.324456f, -0.3f,
            -0.450274f, 0.33055f, -0.3f,
            -0.450272f, 0.330608f, -0.3f,
            -0.450260f, 0.330768f, -0.3f,
            -0.450224f, 0.331009f, -0.3f,
            -0.450155f, 0.331312f, -0.3f,
            -0.450039f, 0.331656f, -0.3f,
            -0.449866f, 0.33202f, -0.3f,
            -0.449625f, 0.332384f, -0.3f,
            -0.449302f, 0.332727f, -0.3f,
            -0.448888f, 0.33303f, -0.3f,
            -0.448371f, 0.333272f, -0.3f,
            -0.447738f, 0.333431f, -0.3f,

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


    public RHTopWinI(){
        this.initVertexBuff(lineCoords);
        this.initListBuff(drawOrder);
    }
}
