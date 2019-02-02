package com.lnl.montorhome;

/**
 * Created by jim on 25/1/2559.
 */

public class LHBody extends BaseShape {

    float lineCoords[] = {
            0.703776f, -0.281794f, 0.3f,
            -0.252389f, -0.281794f, 0.3f,
            -0.250562f, 0.123983f, 0.3f,
            -0.250659f, 0.13093f, 0.3f,
            -0.251007f, 0.136976f, 0.3f,
            -0.251693f, 0.142178f, 0.3f,
            -0.252803f, 0.146591f, 0.3f,
            -0.254421f, 0.150274f, 0.3f,
            -0.256636f, 0.153282f, 0.3f,
            -0.259532f, 0.155672f, 0.3f,
            -0.263196f, 0.1575f, 0.3f,
            -0.267713f, 0.158824f, 0.3f,
            -0.273171f, 0.159699f, 0.3f,
            -0.279654f, 0.160183f, 0.3f,
            -0.287249f, 0.160331f, 0.3f,
            -0.290324f, 0.160331f, 0.3f,
            -0.299016f, 0.160331f, 0.3f,
            -0.312522f, 0.160331f, 0.3f,
            -0.330040f, 0.160331f, 0.3f,
            -0.350767f, 0.160331f, 0.3f,
            -0.373901f, 0.160331f, 0.3f,
            -0.398639f, 0.160331f, 0.3f,
            -0.424180f, 0.160331f, 0.3f,
            -0.449721f, 0.160331f, 0.3f,
            -0.474459f, 0.160331f, 0.3f,
            -0.497593f, 0.160331f, 0.3f,
            -0.518320f, 0.160331f, 0.3f,
            -0.521043f, 0.160345f, 0.3f,
            -0.523521f, 0.160406f, 0.3f,
            -0.525788f, 0.160546f, 0.3f,
            -0.527875f, 0.160796f, 0.3f,
            -0.529815f, 0.161187f, 0.3f,
            -0.531640f, 0.16175f, 0.3f,
            -0.533383f, 0.162517f, 0.3f,
            -0.535075f, 0.163518f, 0.3f,
            -0.536749f, 0.164785f, 0.3f,
            -0.538437f, 0.166349f, 0.3f,
            -0.540171f, 0.16824f, 0.3f,
            -0.541984f, 0.170491f, 0.3f,
            -0.542668f, 0.171287f, 0.3f,
            -0.544599f, 0.173535f, 0.3f,
            -0.547599f, 0.17703f, 0.3f,
            -0.551491f, 0.181562f, 0.3f,
            -0.556096f, 0.186924f, 0.3f,
            -0.561235f, 0.192909f, 0.3f,
            -0.566731f, 0.199309f, 0.3f,
            -0.572406f, 0.205917f, 0.3f,
            -0.578080f, 0.212525f, 0.3f,
            -0.583576f, 0.218925f, 0.3f,
            -0.588715f, 0.22491f, 0.3f,
            -0.593320f, 0.230273f, 0.3f,
            -0.597006f, 0.235962f, 0.3f,
            -0.599888f, 0.241413f, 0.3f,
            -0.601979f, 0.24666f, 0.3f,
            -0.603292f, 0.25174f, 0.3f,
            -0.603842f, 0.256688f, 0.3f,
            -0.603639f, 0.261538f, 0.3f,
            -0.602699f, 0.266328f, 0.3f,
            -0.601034f, 0.271092f, 0.3f,
            -0.598657f, 0.275866f, 0.3f,
            -0.595582f, 0.280685f, 0.3f,
            -0.591821f, 0.285586f, 0.3f,
            -0.587389f, 0.290603f, 0.3f,
            -0.586138f, 0.291692f, 0.3f,
            -0.582603f, 0.29477f, 0.3f,
            -0.577111f, 0.299553f, 0.3f,
            -0.569987f, 0.305756f, 0.3f,
            -0.561558f, 0.313096f, 0.3f,
            -0.552150f, 0.321288f, 0.3f,
            -0.542090f, 0.330049f, 0.3f,
            -0.531703f, 0.339094f, 0.3f,
            -0.521316f, 0.348138f, 0.3f,
            -0.511256f, 0.356899f, 0.3f,
            -0.501848f, 0.365091f, 0.3f,
            -0.493419f, 0.372431f, 0.3f,
            0.092221f, 0.372431f, 0.3f,
            0.189827f, 0.312187f, 0.3f,
            0.688499f, 0.312187f, 0.3f,
            0.696972f, 0.311537f, 0.3f,
            0.705073f, 0.309847f, 0.3f,
            0.712738f, 0.307182f, 0.3f,
            0.719899f, 0.303606f, 0.3f,
            0.726489f, 0.299184f, 0.3f,
            0.732443f, 0.293981f, 0.3f,
            0.737693f, 0.288062f, 0.3f,
            0.742174f, 0.281491f, 0.3f,
            0.745818f, 0.274334f, 0.3f,
            0.748559f, 0.266656f, 0.3f,
            0.750331f, 0.25852f, 0.3f,
            0.751066f, 0.249993f, 0.3f,
            0.751066f, 0.24593f, 0.3f,
            0.751066f, 0.234449f, 0.3f,
            0.751066f, 0.216608f, 0.3f,
            0.751066f, 0.193468f, 0.3f,
            0.751066f, 0.166089f, 0.3f,
            0.751066f, 0.135531f, 0.3f,
            0.751066f, 0.102853f, 0.3f,
            0.751066f, 0.069115f, 0.3f,
            0.751066f, 0.035377f, 0.3f,
            0.751066f, 0.002699f, 0.3f,
            0.751066f, -0.02786f, 0.3f,
            0.751066f, -0.055239f, 0.3f,
            0.751630f, -0.062707f, 0.3f,
            0.751851f, -0.069786f, 0.3f,
            0.751757f, -0.076546f, 0.3f,
            0.751372f, -0.083058f, 0.3f,
            0.750721f, -0.089396f, 0.3f,
            0.749829f, -0.09563f, 0.3f,
            0.748722f, -0.101833f, 0.3f,
            0.747424f, -0.108075f, 0.3f,
            0.745962f, -0.114429f, 0.3f,
            0.744359f, -0.120967f, 0.3f,
            0.742642f, -0.127759f, 0.3f,
            0.740835f, -0.134879f, 0.3f,
            0.740342f, -0.136834f, 0.3f,
            0.738948f, -0.14236f, 0.3f,
            0.736782f, -0.150947f, 0.3f,
            0.733973f, -0.162085f, 0.3f,
            0.730649f, -0.175263f, 0.3f,
            0.726938f, -0.189972f, 0.3f,
            0.722971f, -0.205701f, 0.3f,
            0.718875f, -0.22194f, 0.3f,
            0.714778f, -0.238179f, 0.3f,
            0.710811f, -0.253907f, 0.3f,
            0.707101f, -0.268616f, 0.3f,

    };
    short drawOrder[] = { 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
            11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
            21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
            31, 32, 33, 34, 35, 36, 37, 38, 39, 40,
            41, 42, 43, 44, 45, 46, 47, 48, 49, 50,
            51, 52, 53, 54, 55, 56, 57, 58, 59, 60,
            61, 62, 63, 64, 65, 66, 67, 68, 69, 70,
            71, 72, 73, 74, 75, 76, 77, 78, 79, 80,
            81, 82, 83, 84, 85, 86, 87, 88, 89, 90,
            91, 92, 93, 94, 95, 96, 97, 98, 99, 100,
            101, 102, 103, 104, 105, 106, 107, 108, 109, 110,
            111, 112, 113, 114, 115, 116, 117, 118, 119, 120,
            121, 122
    }; // order to draw verticies

    public LHBody(){
        this.initVertexBuff(lineCoords);
        this.initListBuff(drawOrder);
    }
}