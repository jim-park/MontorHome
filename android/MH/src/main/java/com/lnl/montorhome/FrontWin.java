package com.lnl.montorhome;

/**
 * Created by jim on 25/1/2559.
 */

public class FrontWin extends BaseShape {

    float lineCoords[] = {

            -0.595582f, 0.280685f, -0.2f,
            -0.595582f, 0.280685f, 0.2f,
            -0.511256f, 0.356899f, 0.2f,
            -0.511256f, 0.356899f, -0.2f,
    };
    short drawOrder[] = { 0, 1, 2, 3, 0 }; // order to draw verticies

    public FrontWin(){
        this.initVertexBuff(lineCoords);
        this.initListBuff(drawOrder);
    }
}