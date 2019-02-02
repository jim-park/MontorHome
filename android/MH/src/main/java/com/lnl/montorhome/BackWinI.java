package com.lnl.montorhome;

/**
 * Created by jim on 8/2/2559.
 */
public class BackWinI extends BaseShape {

    float lineCoords[] =  {

            0.751071f, 0.17119f, 0.15f,   // Top Left
            0.751071f, 0.018934f, 0.15f,  // Bot Left
            0.751071f, 0.018934f, -0.15f, // Bot Right
            0.751071f, 0.17119f,  -0.15f  // Top Right
    };

    short drawOrder[] = { 0, 1, 2, 3 };

    public BackWinI() {
        this.initVertexBuff(lineCoords);
        this.initListBuff(drawOrder);
    }
}
