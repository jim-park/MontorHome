package com.opengl_test.jim.opengl_test;

import android.opengl.GLES20;

import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.nio.FloatBuffer;
import java.nio.ShortBuffer;

/**
 * Created by jim on 25/1/2559.
 */


public class Square {

    private FloatBuffer vertexBuffer;
    private ShortBuffer drawListBuffer;
    private final int mProgram;
    private int mPositionHandle;

    private int mColorHandle;
    static final int COORDS_PER_VERTEX = 3;     // Number of coordinates per vertex in this array
    float color[] = { 0.63671875f, 0.76953125f, 0.22265625f, 1.0f }; // Set the colour with red, green blue and alpha (opacity) values
    float squareCoords[] = {          // in counter clockwise order
            -0.5f,  0.5f, 0.0f, // top left
            -0.5f, -0.5f, 0.0f, // bottom left
             0.5f, -0.5f, 0.0f, // bottom right
             0.5f,  0.5f, 0.0f  // top right
    };

    private short drawOrder[] = {0, 1, 2, 0, 2, 3}; // order to draw verticies

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
    private final int vertexCount = squareCoords.length / COORDS_PER_VERTEX;
    private final int vertexStride = COORDS_PER_VERTEX * 4; // 4 bytes per vertex
    // Use to access anf set the view transformations
    private int mMVPMatrixHandle;

    public Square() {

        // initialise vertex byte buffer for shape coordinates
        ByteBuffer bb = ByteBuffer.allocateDirect(
                // number of coorinate values * 4 bytes per float
                squareCoords.length * 4 );
        // use the hardwares native byte order
        bb.order(ByteOrder.nativeOrder());

        // create a floating point buffer from the ByteBuffer
        vertexBuffer = bb.asFloatBuffer();
        // add the coordinates to the FloatBuffer
        vertexBuffer.put(squareCoords);
        // set the buffer to read the first coordinates
        vertexBuffer.position(0);

        // initialise byte buffer for the draw list
        ByteBuffer dlb = ByteBuffer.allocateDirect(drawOrder.length * 2); // short is 2 bytes
        dlb.order(ByteOrder.nativeOrder());
        drawListBuffer = dlb.asShortBuffer();
        drawListBuffer.put(drawOrder);
        drawListBuffer.position(0);

        int vertexShader = MyGLRenderer.loadShader(GLES20.GL_VERTEX_SHADER, vertexShaderCode);
        int fragmentShader = MyGLRenderer.loadShader(GLES20.GL_FRAGMENT_SHADER, fragmentShaderCode);

        // Create empty openGL ES program
        mProgram = GLES20.glCreateProgram();
        MyGLRenderer.checkGlError("glCreateProgram");

        // add the vertex shader to the program
        GLES20.glAttachShader(mProgram, vertexShader);
        MyGLRenderer.checkGlError("glAttachShader");

        // add the fragment shader to the program
        GLES20.glAttachShader(mProgram, fragmentShader);
        MyGLRenderer.checkGlError("glAttachShader");

        // creates OpenGL ES program executables
        GLES20.glLinkProgram(mProgram);
        MyGLRenderer.checkGlError("glLinkProgram");

    }

    public void draw(float[] mvpMatrix) { // Pass in calculated xform matrix
        // Add program to OpenGL ES enviroment
        GLES20.glUseProgram(mProgram);

        // get handle to vertex shaders vPosition member
        mPositionHandle = GLES20.glGetAttribLocation(mProgram, "vPosition");

        // Enable a handle to the trianlge verticies
        GLES20.glEnableVertexAttribArray(mPositionHandle);

        // Prepare the square coodinate data
        GLES20.glVertexAttribPointer(mPositionHandle, COORDS_PER_VERTEX, GLES20.GL_FLOAT,
                false, vertexStride, vertexBuffer);

        // get handle to fragment shaders vColor member
        mColorHandle = GLES20.glGetUniformLocation(mProgram, "vColor");

        // Set color for drawing the square
        GLES20.glUniform4fv(mColorHandle, 1, color, 0);

        // get handle to shapes xformation matrix
        mMVPMatrixHandle = GLES20.glGetUniformLocation(mProgram, "uMVPMatrix");

        // Pass the projection and view xformation to the view shader
        GLES20.glUniformMatrix4fv(mMVPMatrixHandle, 1, false, mvpMatrix, 0);

        // Draw the square
        GLES20.glDrawElements(GLES20.GL_TRIANGLES, drawOrder.length, GLES20.GL_UNSIGNED_SHORT, drawListBuffer);

        // Disable the vertex array
        GLES20.glDisableVertexAttribArray(mPositionHandle);
    }
}