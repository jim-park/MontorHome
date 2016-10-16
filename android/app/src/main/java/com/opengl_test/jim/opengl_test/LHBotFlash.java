package com.opengl_test.jim.opengl_test;

/**
 * Created by jim on 8/2/2559.
 */
public class LHBotFlash extends BaseShape {


    float lineCoords[] =  {

            -0.252249f, -0.228756f, 0.3f,
            0.716450f, -0.230319f, 0.3f,

    };

    short drawOrder[] = {  0, 1 };

    public LHBotFlash(){
        this.initVertexBuff(lineCoords);
        this.initListBuff(drawOrder);
    }
}
