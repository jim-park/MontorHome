package com.opengl_test.jim.opengl_test;

import android.opengl.GLES20;

import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.nio.FloatBuffer;
import java.nio.ShortBuffer;

/**
 * Created by jim on 25/1/2559.
 */


public class Lines {

    private FloatBuffer vertexBuffer;
    private ShortBuffer drawListBuffer;
    private final int mProgram;
    private int mPositionHandle;
    private int mColorHandle;
    static final int COORDS_PER_VERTEX = 3;                 // Number of coordinates per vertex in this array
    private final int vertexStride = COORDS_PER_VERTEX * 4; // 4 bytes per vertex
    float color[] = { 0, 1, 0, 1.0f };                      // Set the colour with red, green blue and alpha (opacity) values
    float lineCoords[] = {
                        0.55f,  0.55f,  0.55f,  //0 top right front
                       -0.55f,  0.55f,  0.55f,  //1 top left front
                        0.55f, -0.55f,  0.55f,  //2 bottom right front
                       -0.55f, -0.55f,  0.55f,  //3 bottom left front
            
                        0.55f,  0.55f, -0.55f,  //4 top right back
                       -0.55f,  0.55f, -0.55f,  //5 top left back
                        0.55f, -0.55f, -0.55f,  //6 bottom right back
                       -0.55f, -0.55f, -0.55f   //7 bottom left back
    };

    private short drawOrder[] = {1, 3, 2, 0, 1, 5, 4, 6, 7, 3, 2, 6, 7, 5, 4, 0}; // order to draw verticies

    private final String vertexShaderCode =
                    "uniform mat4 uMVPMatrix;" +
                    "attribute vec4 vPosition;" +
                    "void main() {" +
                    "  gl_Position = uMVPMatrix * vPosition;" +
                    "}";
    private final String fragmentShaderCode =
            "precision mediump float;" +
                    "uniform vec4 vColor;" +
                    "void main() {" +
                    "  gl_FragColor = vColor;" +
                    "}";
    // Use to access anf set the view transformations
    private int mMVPMatrixHandle;

    public Lines() {

        // initialise vertex byte buffer for shape coordinates
        ByteBuffer bb = ByteBuffer.allocateDirect(lineCoords.length * 4 );
        bb.order(ByteOrder.nativeOrder());
        vertexBuffer = bb.asFloatBuffer();
        vertexBuffer.put(lineCoords);
        vertexBuffer.position(0);

        // initialise byte buffer for the draw list
        ByteBuffer dlb = ByteBuffer.allocateDirect(drawOrder.length * 2); // short is 2 bytes
        dlb.order(ByteOrder.nativeOrder());
        drawListBuffer = dlb.asShortBuffer();
        drawListBuffer.put(drawOrder);
        drawListBuffer.position(0);

        int vertexShader = MyGLRenderer.loadShader(GLES20.GL_VERTEX_SHADER, vertexShaderCode);
        int fragmentShader = MyGLRenderer.loadShader(GLES20.GL_FRAGMENT_SHADER, fragmentShaderCode);

        mProgram = GLES20.glCreateProgram();                // Create empty openGL ES program
        MyGLRenderer.checkGlError("glCreateProgram");
        GLES20.glAttachShader(mProgram, vertexShader);      // add the vertex shader to the program
        MyGLRenderer.checkGlError("glAttachShader");
        GLES20.glAttachShader(mProgram, fragmentShader);    // add the fragment shader to the program
        MyGLRenderer.checkGlError("glAttachShader");
        GLES20.glLinkProgram(mProgram);                     // creates OpenGL ES program executables
        MyGLRenderer.checkGlError("glLinkProgram");

    }

    public void draw(float[] mvpMatrix) { // Pass in calculated xform matrix
        // Add program to OpenGL ES enviroment
        GLES20.glUseProgram(mProgram);

        // get handle to vertex shaders vPosition member
        mPositionHandle = GLES20.glGetAttribLocation(mProgram, "vPosition");
        // Enable a handle to the line verticies
        GLES20.glEnableVertexAttribArray(mPositionHandle);
        // Prepare the triangle coodinate data
        GLES20.glVertexAttribPointer(mPositionHandle, COORDS_PER_VERTEX, GLES20.GL_FLOAT,
                false, vertexStride, vertexBuffer);
        // get handle to fragment shaders vColor member
        mColorHandle = GLES20.glGetUniformLocation(mProgram, "vColor");
        // Set color for drawing the lines
        GLES20.glUniform4fv(mColorHandle, 1, color, 0);
        // get handle to shapes xformation matrix
        mMVPMatrixHandle = GLES20.glGetUniformLocation(mProgram, "uMVPMatrix");
        // Pass the projection and view xformation to the view shader
        GLES20.glUniformMatrix4fv(mMVPMatrixHandle, 1, false, mvpMatrix, 0);

        // Draw the lines
        GLES20.glDrawElements(GLES20.GL_LINE_LOOP, drawOrder.length, GLES20.GL_UNSIGNED_SHORT, drawListBuffer);

        // Disable the vertex array
        GLES20.glDisableVertexAttribArray(mPositionHandle);
    }
}