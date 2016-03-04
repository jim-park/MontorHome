package com.opengl_test.jim.opengl_test;

import android.graphics.Matrix;
import android.opengl.GLES10;
import android.opengl.GLES20;
import android.opengl.GLSurfaceView;

import javax.microedition.khronos.egl.EGLConfig;
import javax.microedition.khronos.opengles.GL10;

import android.os.SystemClock;
import android.util.Log;
import android.view.Display;
import android.content.res.Configuration;
import android.view.WindowManager;
import android.view.Surface;
import android.content.Context;
import android.app.Activity;

/**
 * Created by jim on 25/1/2559.
 */
public class MyGLRenderer implements GLSurfaceView.Renderer {

    private static final String     TAG = "MyGLRenderer";
    private LHBody                  mLHBody;
    private LHDoor                  mLHDoor;
    private LHCab                   mLHCab;
    private LHCabWin                mLHCabWin;
    private LHMainWinI              mLHMainWinI;
    private LHMainWinO              mLHMainWinO;
    private LHTopWinI               mLHTopWinI;
    private RHBotFlash              mRHBotFlash;
    private LHBotFlash              mLHBotFlash;
    private RHBody                  mRHBody;
    private RHCab                   mRHCab;
    private RHDoor                  mRHDoor;
    private RHCabWin                mRHCabWin;
    private RHMainWinI              mRHMainWinI;
    private RHMainWinO              mRHMainWinO;
    private RHTopWinI               mRHTopWinI;
    private RHGasStore              mRHGasStore;
    private RHGasCatch              mRHGasCatch;
    private LHStoreO                mLHStoreO;
    private LHStoreI                mLHStoreI;
    private LHStoreCatch            mLHStoreCatch;
    private BackWinI                mBackWinI;
    private FrontWin                mFrontWin;
    private final float[]           mMVPMatrix = new float[16];
    private final float[]           mProjectionMatrix = new float[16];
    private final float[]           mViewMatrix = new float[16];
    private final float[]           mRotationMatrix = new float[16];
    private int orientation;
    public volatile float           mAngle;

    public static int isAlertMainLHWin = 0;

    float red = 1.0f;
    float prev_red = red;
    float l_width = 5.0f;


    public MyGLRenderer(int orientation) {
        super();
        this.orientation = orientation;
        Log.i(TAG, "Constructor orientation: " + this.orientation);
    }

    @Override
    public void onSurfaceCreated(GL10 gl, EGLConfig config) {
        // Set the background frame color
        GLES20.glClearColor(0.0f, 0.0f, 0.0f, 1.0f);
        MyGLRenderer.checkGlError("glClearColor");

        // Initialise bits
        // Lefts
        mLHBody       = new LHBody();
        mLHCab        = new LHCab();
        mLHDoor       = new LHDoor();
        mLHCabWin     = new LHCabWin();
        mLHMainWinI   = new LHMainWinI();
        mLHMainWinO   = new LHMainWinO();
        mLHTopWinI    = new LHTopWinI();
        mLHStoreCatch = new LHStoreCatch();
        mLHStoreO     = new LHStoreO();
        mLHStoreI     = new LHStoreI();
        mLHBotFlash   = new LHBotFlash();
        // Rights
        mRHBody       = new RHBody();
        mRHCab        = new RHCab();
        mRHDoor       = new RHDoor();
        mRHCabWin     = new RHCabWin();
        mRHMainWinO   = new RHMainWinO();
        mRHTopWinI    = new RHTopWinI();
        mRHBotFlash   = new RHBotFlash();
        mRHMainWinI   = new RHMainWinI();
        mRHGasStore   = new RHGasStore();
        mRHGasCatch   = new RHGasCatch();

        mBackWinI     = new BackWinI();
        mFrontWin     = new FrontWin();

//      Log.e(TAG, "onSurfaceCreated: called");
//        Display display = ((WindowManager) this.getContext().getSystemService(Context.WINDOW_SERVICE)).getDefaultDisplay();
//        int orientation = display.getRotation();
    }

    @Override
    public void onDrawFrame(GL10 gl) {
        float[] scratch = new float[16];

        // Redraw background color
        GLES20.glClear(GLES20.GL_COLOR_BUFFER_BIT);
        MyGLRenderer.checkGlError("glClear");


        // make bigger for wide view
        if ( this.orientation == 1 || this.orientation == 3) {
            // Set the camera position (View matrix)
//            Log.e(TAG, "onDrawFram: move camera back");
            android.opengl.Matrix.setLookAtM(mViewMatrix, 0, 0, 0, 5f, 0f, 0f, 0f, 0f, 1.0f, 0.0f);
        } else {
            // Set the camera position (View matrix)
            android.opengl.Matrix.setLookAtM(mViewMatrix, 0, 0, 0, 5, 0f, 0f, 0f, 0f, 1.0f, 0.0f);
        }
        // Calculate the projection and view transformation
        android.opengl.Matrix.multiplyMM(mMVPMatrix, 0, mProjectionMatrix, 0, mViewMatrix, 0);

        // Create a rotation transformation for the triangle
//        long time = SystemClock.uptimeMillis() % 4000L;
//        float angle = 0.090f * ((int) time);
        android.opengl.Matrix.setRotateM(mRotationMatrix, 0, mAngle, 0.0f, -0.5f, 0.0f);


        // Combine the rotation matrix with the projection and camera view
        // Note that the mMVPMatrix factor *must be first* in order
        // for the matrix multiplication product to be correct.
        android.opengl.Matrix.multiplyMM(scratch, 0, mMVPMatrix, 0, mRotationMatrix, 0);


        // Draw chassis
        mLHBody.draw(scratch, 0);
        mRHBody.draw(scratch, 0);
        mLHDoor.draw(scratch, 0);
        mRHDoor.draw(scratch, 0);
        mLHCab.draw(scratch, 0);
        mRHCab.draw(scratch, 0);
        mLHCabWin.draw(scratch, 0);
        mRHCabWin.draw(scratch, 0);
        mLHBotFlash.draw(scratch, 0);
        mRHBotFlash.draw(scratch, 0);
        mFrontWin.draw(scratch, 0);

        // Alertable
        mLHMainWinO.draw(scratch, isAlertMainLHWin);
        mLHMainWinI.draw(scratch, isAlertMainLHWin);
        mLHTopWinI.draw(scratch, 0);
        mLHStoreO.draw(scratch, 0);
        mLHStoreI.draw(scratch, 0);
        mLHStoreCatch.draw(scratch, 0);
        mRHMainWinO.draw(scratch, 0);
        mRHMainWinI.draw(scratch, 0);
        mRHTopWinI.draw(scratch, 0);
        mRHGasStore.draw(scratch, 0);
        mRHGasCatch.draw(scratch, 0);
        mBackWinI.draw(scratch, 0);

       // Log.e(TAG, "onDrawFrame: called [red: " + red + "]");

    }

    @Override
    public void onSurfaceChanged(GL10 gl, int width, int height) {
        GLES20.glViewport(0, 0, width, height);
        MyGLRenderer.checkGlError("glViewPort");

        float ratio = (float) width / height;
        // This projection Matrix is applied to object coordinates
        // in the onDrawFrame method.

        // make bigger for wide view
        if ( this.orientation == 1 || this.orientation == 3 ) {
//            Log.e(TAG, "onDrawFrame: scaled Proj Matrix");
//            Log.e(TAG, "onDrawFrame: ratio: "  + ratio + ", left: " + (-ratio+1) + ", right: " + (ratio-1));
            android.opengl.Matrix.frustumM(mProjectionMatrix, 0, -ratio + 1, ratio - 1, -0.5f, 0.5f, 4, 7);
        } else {
            android.opengl.Matrix.frustumM(mProjectionMatrix, 0, -ratio, ratio, -1, 1, 3, 7);
        }
        Log.i(TAG, "onSurfaceChanged: called");
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

    public float getAngle() {
        return mAngle;
    }

    public void setAngle(float angle) {
        mAngle = angle;
    }

    public static void setAlertMainLHWin(boolean alert_flg) {
        isAlertMainLHWin = (alert_flg) ? 1 : 0;
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


