package com.opengl_test.jim.opengl_test;

import android.graphics.Matrix;
import android.opengl.GLES20;
import android.opengl.GLSurfaceView;

import javax.microedition.khronos.egl.EGLConfig;
import javax.microedition.khronos.opengles.GL10;

import android.os.SystemClock;
import android.util.Log;

/**
 * Created by jim on 25/1/2559.
 */
public class MyGLRenderer implements GLSurfaceView.Renderer {

    private static final String TAG = "MyGLRenderer";
    private Triangle mTriangle;
    private Lines mLines;
    private Square mSquare;
    private final float[] mMVPMatrix = new float[16];
    private final float[] mProjectionMatrix = new float[16];
    private final float[] mViewMatrix = new float[16];
    private final float[] mRotationMatrix = new float[16];

    @Override
    public void onSurfaceCreated(GL10 gl, EGLConfig config) {
        // Set the background frame color
        GLES20.glClearColor(0.0f, 0.0f, 0.0f, 1.0f);
        MyGLRenderer.checkGlError("glClearColor");
        // Initialise a Triangle
        mTriangle   = new Triangle();
        mLines      = new Lines();
        mSquare     = new Square();
    }

    @Override
    public void onDrawFrame(GL10 gl) {
        float[] scratch = new float[16];

        // Redraw background color
        GLES20.glClear(GLES20.GL_COLOR_BUFFER_BIT);
        MyGLRenderer.checkGlError("glClear");

        // Set the camera position (View matrix)
        android.opengl.Matrix.setLookAtM(mViewMatrix, 0, 0, 0, 6, 0f, 0f, 0f, 0f, 1.0f, 0.0f);

        // Calculate the projection and view transformation
        android.opengl.Matrix.multiplyMM(mMVPMatrix, 0, mProjectionMatrix, 0, mViewMatrix, 0);

        // Create a rotation transformation for the triangle
        long time = SystemClock.uptimeMillis() % 4000L;
        float angle = 0.090f * ((int) time);
        android.opengl.Matrix.setRotateM(mRotationMatrix, 0, angle, 0.5f, -1.0f, 0.2f);


        // Combine the rotation matrix with the projection and camera view
        // Note that the mMVPMatrix factor *must be first* in order
        // for the matrix multiplication product to be correct.
        android.opengl.Matrix.multiplyMM(scratch, 0, mMVPMatrix, 0, mRotationMatrix, 0);

//        mSquare.draw(scratch);
        mLines.draw(scratch);
//        mSquare.draw(mMVPMatrix);
//        mTriangle.draw(scratch);
    }

    @Override
    public void onSurfaceChanged(GL10 unused, int width, int height) {
        GLES20.glViewport(0, 0, width, height);
        MyGLRenderer.checkGlError("glViewPort");

        float ratio = (float) width / height;

        // This projection Matrix is applied to object coordinates
        // in the onDrawFrame method.
        android.opengl.Matrix.frustumM(mProjectionMatrix, 0, -ratio, ratio, -1, 1, 3, 7);
    }

    public static int loadShader(int type, String shaderCode) {

        // create a vertex shader type (GLES20.GL_VERTEX_SHADER)
        // or a fragment shader type (GLES20.GL_FRAGMENT_SHADER)
        int shader = GLES20.glCreateShader(type);
        MyGLRenderer.checkGlError("glCreateShader");

        // add the source code to the shader and compile it
        GLES20.glShaderSource(shader, shaderCode);
        MyGLRenderer.checkGlError("glShaderSource");
        GLES20.glCompileShader(shader);
        MyGLRenderer.checkGlError("glCompileShader");

        return shader;
    }

   /**
    * Utility method for debugging OpenGL calls. Provide the name of the call
    * just after making it:
    *
    * <pre>
    * mColorHandle = GLES20.glGetUniformLocation(mProgram, "vColor");
    * MyGLRenderer.checkGlError("glGetUniformLocation");</pre>
    *
    * If the operation is not successful, the check throws an error.
    *
    * @param glOperation - Name of the OpenGL call to check.
    */
    public static void checkGlError(String glOperation) {
        int error;
        while ((error = GLES20.glGetError()) != GLES20.GL_NO_ERROR) {
            Log.e(TAG, glOperation + ": glError " + error);
            throw new RuntimeException(glOperation + ": glError " + error);
        }
    }
}


