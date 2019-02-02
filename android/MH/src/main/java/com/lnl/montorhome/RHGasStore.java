package com.lnl.montorhome;

/**
 * Created by jim on 8/2/2559.
 */
public class RHGasStore extends BaseShape {


    float lineCoords[] =  {
            -0.237065f, -0.152532f, -0.3f,
            -0.237065f, -0.22885f, -0.3f,
            -0.251856f, -0.228629f, -0.3f,
            -0.251856f, -0.281465f, -0.3f,
            -0.095549f, -0.281465f, -0.3f,
            -0.095549f, -0.229292f, -0.3f,
            -0.110585f, -0.229292f, -0.3f,
            -0.110585f, -0.153783f, -0.3f,
            -0.110694f, -0.151716f, -0.3f,
            -0.111023f, -0.149756f, -0.3f,
            -0.111572f, -0.147917f, -0.3f,
            -0.112342f, -0.146213f, -0.3f,
            -0.113335f, -0.144658f, -0.3f,
            -0.114551f, -0.143265f, -0.3f,
            -0.115992f, -0.142048f, -0.3f,
            -0.117658f, -0.141022f, -0.3f,
            -0.119552f, -0.140199f, -0.3f,
            -0.121673f, -0.139595f, -0.3f,
            -0.124022f, -0.139222f, -0.3f,
            -0.126602f, -0.139094f, -0.3f,
            -0.127867f, -0.139094f, -0.3f,
            -0.131443f, -0.139094f, -0.3f,
            -0.137000f, -0.139094f, -0.3f,
            -0.144206f, -0.139094f, -0.3f,
            -0.152733f, -0.139094f, -0.3f,
            -0.162251f, -0.139094f, -0.3f,
            -0.172428f, -0.139094f, -0.3f,
            -0.182936f, -0.139094f, -0.3f,
            -0.193444f, -0.139094f, -0.3f,
            -0.203621f, -0.139094f, -0.3f,
            -0.213138f, -0.139094f, -0.3f,
            -0.221666f, -0.139094f, -0.3f,
            -0.223745f, -0.139175f, -0.3f,
            -0.225743f, -0.139421f, -0.3f,
            -0.227640f, -0.13984f, -0.3f,
            -0.229417f, -0.140438f, -0.3f,
            -0.231056f, -0.141223f, -0.3f,
            -0.232537f, -0.142201f, -0.3f,
            -0.233842f, -0.14338f, -0.3f,
            -0.234952f, -0.144767f, -0.3f,
            -0.235848f, -0.146369f, -0.3f,
            -0.236511f, -0.148192f, -0.3f,
            -0.236923f, -0.150244f, -0.3f,
    };

    short drawOrder[] = {  0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
                            11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
                            21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
                            31, 32, 33, 34, 35, 36, 37, 38, 39, 40,
                            41, 42,
                        };


    public RHGasStore(){
        this.initVertexBuff(lineCoords);
        this.initListBuff(drawOrder);
    }
}
