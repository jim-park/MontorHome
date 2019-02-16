package com.lnl.montorhome;

/**
 * Created by James Park
 * email: jim@linuxnetworks.co.uk
 * Date: 8/2/2559.
 */
public class LHStoreO extends BaseShape {

    float lineCoords[] =  {
            -0.004402f, -0.140199f, 0.3f,
            -0.001878f, -0.140379f, 0.3f,
            0.000543f, -0.140903f, 0.3f,
            0.002838f, -0.141748f, 0.3f,
            0.004986f, -0.142891f, 0.3f,
            0.006964f, -0.144307f, 0.3f,
            0.008750f, -0.145973f, 0.3f,
            0.010323f, -0.147866f, 0.3f,
            0.011659f, -0.149963f, 0.3f,
            0.012736f, -0.152239f, 0.3f,
            0.013534f, -0.154672f, 0.3f,
            0.014028f, -0.157237f, 0.3f,
            0.014198f, -0.159912f, 0.3f,
            -0.003441f, -0.140252f, 0.3f,
            -0.212859f, -0.140252f, 0.3f,
            -0.214858f, -0.140573f, 0.3f,
            -0.216703f, -0.141015f, 0.3f,
            -0.218393f, -0.14159f, 0.3f,
            -0.219931f, -0.142308f, 0.3f,
            -0.221317f, -0.143177f, 0.3f,
            -0.222553f, -0.144209f, 0.3f,
            -0.223639f, -0.145413f, 0.3f,
            -0.224578f, -0.146799f, 0.3f,
            -0.225369f, -0.148378f, 0.3f,
            -0.226015f, -0.150159f, 0.3f,
            -0.226516f, -0.152152f, 0.3f,
            -0.226874f, -0.154368f, 0.3f,
            -0.226874f, -0.155077f, 0.3f,
            -0.226874f, -0.157078f, 0.3f,
            -0.226874f, -0.160189f, 0.3f,
            -0.226874f, -0.164224f, 0.3f,
            -0.226874f, -0.168997f, 0.3f,
            -0.226874f, -0.174326f, 0.3f,
            -0.226874f, -0.180023f, 0.3f,
            -0.226874f, -0.185906f, 0.3f,
            -0.226874f, -0.191788f, 0.3f,
            -0.226874f, -0.197486f, 0.3f,
            -0.226874f, -0.202814f, 0.3f,
            -0.226874f, -0.207588f, 0.3f,
            -0.226591f, -0.209619f, 0.3f,
            -0.226100f, -0.211637f, 0.3f,
            -0.225403f, -0.213613f, 0.3f,
            -0.224498f, -0.215524f, 0.3f,
            -0.223387f, -0.217342f, 0.3f,
            -0.222070f, -0.219042f, 0.3f,
            -0.220546f, -0.220597f, 0.3f,
            -0.218817f, -0.221983f, 0.3f,
            -0.216883f, -0.223172f, 0.3f,
            -0.214744f, -0.22414f, 0.3f,
            -0.212401f, -0.224859f, 0.3f,
            -0.209853f, -0.225305f, 0.3f,
            -0.207084f, -0.225305f, 0.3f,
            -0.199260f, -0.225305f, 0.3f,
            -0.187102f, -0.225305f, 0.3f,
            -0.171333f, -0.225305f, 0.3f,
            -0.152675f, -0.225305f, 0.3f,
            -0.131851f, -0.225305f, 0.3f,
            -0.109581f, -0.225305f, 0.3f,
            -0.086590f, -0.225305f, 0.3f,
            -0.063599f, -0.225305f, 0.3f,
            -0.041329f, -0.225305f, 0.3f,
            -0.020505f, -0.225305f, 0.3f,
            -0.001846f, -0.225305f, 0.3f,
            0.000949f, -0.22474f, 0.3f,
            0.003406f, -0.22404f, 0.3f,
            0.005547f, -0.223193f, 0.3f,
            0.007394f, -0.222191f, 0.3f,
            0.008969f, -0.221025f, 0.3f,
            0.010292f, -0.219684f, 0.3f,
            0.011386f, -0.218159f, 0.3f,
            0.012272f, -0.21644f, 0.3f,
            0.012972f, -0.214518f, 0.3f,
            0.013508f, -0.212384f, 0.3f,
            0.013901f, -0.210027f, 0.3f,
            0.014172f, -0.207438f, 0.3f,
            0.014172f, -0.206789f, 0.3f,
            0.014172f, -0.204957f, 0.3f,
            0.014172f, -0.202109f, 0.3f,
            0.014172f, -0.198416f, 0.3f,
            0.014172f, -0.194045f, 0.3f,
            0.014172f, -0.189168f, 0.3f,
            0.014172f, -0.183952f, 0.3f,
            0.014172f, -0.178567f, 0.3f,
            0.014172f, -0.173182f, 0.3f,
            0.014172f, -0.167966f, 0.3f,
            0.014172f, -0.163088f, 0.3f,
            0.014172f, -0.158718f, 0.3f,
    };

    short drawOrder[] = {  0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
            11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
            21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
            31, 32, 33, 34, 35, 36, 37, 38, 39, 40,
            41, 42, 43, 44, 45, 46, 47, 48, 49, 50,
            51, 52, 53, 54, 55, 56, 57, 58, 59, 60,
            61, 62, 63, 64, 65, 66, 67, 68, 69, 70,
            71, 72, 73, 74, 75, 76, 77, 78, 79, 80,
            81, 82, 83, 84,
                        };


    public LHStoreO(){
        this.initVertexBuff(lineCoords);
        this.initListBuff(drawOrder);
    }
}
