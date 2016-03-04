package com.opengl_test.jim.opengl_test;

import android.opengl.GLES20;
import android.util.Log;

import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.nio.FloatBuffer;
import java.nio.ShortBuffer;

/**
 * Created by jim on 25/1/2559.
 */


public class BaseShape {

    private final String TAG = "BaseShape";
    private FloatBuffer vertexBuffer;
    private ShortBuffer drawListBuffer;
    private final int mProgram;
    private int mPositionHandle;
    private int mColorHandle;
    static final int COORDS_PER_VERTEX = 3;                 // Number of coordinates per vertex in this array
    private final int vertexStride = COORDS_PER_VERTEX * 4; // 4 bytes per vertex
    float obj_color[] = { 0, 1, 0, 1.0f };                      // Set the colour with red, green blue and alpha (opacity) values
    float lineCoords[];
    private short drawOrder[];

    float red = 1.0f;
    float prev_red = red;
    float l_width = 2.0f;

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

    public BaseShape() {

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

    // initialise vertex byte buffer for shape coordinates
    public void initVertexBuff(float[] lineCoords_in) {
        lineCoords = lineCoords_in;
        ByteBuffer bb = ByteBuffer.allocateDirect(lineCoords.length * 4 );
        bb.order(ByteOrder.nativeOrder());
        vertexBuffer = bb.asFloatBuffer();
        vertexBuffer.put(lineCoords);
        vertexBuffer.position(0);
    }

    // initialise byte buffer for the draw list
    public void initListBuff(short[] drawOrder_in) {
        drawOrder = drawOrder_in;
        ByteBuffer dlb = ByteBuffer.allocateDirect(drawOrder.length * 2); // short is 2 bytes
        dlb.order(ByteOrder.nativeOrder());
        drawListBuffer = dlb.asShortBuffer();
        drawListBuffer.put(drawOrder);
        drawListBuffer.position(0);
    }

    public void initColor(float[] color) {
        obj_color = color;
    }

    public void draw( float[] mvpMatrix, int alert ) { // Pass in calculated xform matrix, and alert flag

        if ( alert == 1 ) {
            obj_color[1] = 0;   // Green off
            // counting down
            if ( prev_red > obj_color[0] || obj_color[0] >= 1.0f ) {
                prev_red = obj_color[0];
                l_width = l_width - 0.2f;
                obj_color[0] = obj_color[0] - 0.05f;
            }
            // counting up
            if ( prev_red < obj_color[0] || obj_color[0] <= 0.0f ) {
                prev_red = obj_color[0];
                l_width = l_width + 0.2f;
                obj_color[0] = obj_color[0] + 0.05f;
            }
        } else {
            obj_color[0] = 0; // Red off
            obj_color[1] = 1; // Green on
            obj_color[2] = 0; // Blue off
            l_width = 2.0f;
        }
        
        // Add program to OpenGL ES environment
        GLES20.glUseProgram(mProgram);
        MyGLRenderer.checkGlError("glUseProgram");

        // get handle to vertex shaders vPosition member
        mPositionHandle = GLES20.glGetAttribLocation(mProgram, "vPosition");
        MyGLRenderer.checkGlError("glGetAttribLocation");

        // Enable a handle to the line verticies
        GLES20.glEnableVertexAttribArray(mPositionHandle);
        MyGLRenderer.checkGlError("glEnableVertexAttrib");

        // Prepare the coodinate data
        GLES20.glVertexAttribPointer(mPositionHandle, COORDS_PER_VERTEX, GLES20.GL_FLOAT,
                                        false, vertexStride, vertexBuffer);
        MyGLRenderer.checkGlError("glVertexAttribPointer");

        // get handle to fragment shaders vColor member
        mColorHandle = GLES20.glGetUniformLocation(mProgram, "vColor");
        MyGLRenderer.checkGlError("glGetUniformLocation");

        // Set color for drawing the lines
        GLES20.glUniform4fv(mColorHandle, 1, obj_color, 0);
        MyGLRenderer.checkGlError("glUniform4fv");

        // get handle to shapes transformation matrix
        mMVPMatrixHandle = GLES20.glGetUniformLocation(mProgram, "uMVPMatrix");
        MyGLRenderer.checkGlError("glGetUniformLocation");

        // Pass the projection and view transformation to the view shader
        GLES20.glUniformMatrix4fv(mMVPMatrixHandle, 1, false, mvpMatrix, 0);
        MyGLRenderer.checkGlError("glUniformMatrix4fv");

        // Set the line width
        GLES20.glLineWidth(l_width);
        MyGLRenderer.checkGlError("glLineWidth");

        // Draw the lines
        GLES20.glDrawElements(GLES20.GL_LINE_LOOP, drawOrder.length, GLES20.GL_UNSIGNED_SHORT, drawListBuffer);
        MyGLRenderer.checkGlError("glDrawElements");

        // Disable the vertex array
        GLES20.glDisableVertexAttribArray(mPositionHandle);
        MyGLRenderer.checkGlError("glDisableVertexAttribArray");
    }
}