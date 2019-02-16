package com.lnl.montorhome;

import android.opengl.GLES20;
import android.opengl.GLSurfaceView;

import javax.microedition.khronos.egl.EGLConfig;
import javax.microedition.khronos.opengles.GL10;

import android.util.Log;

import java.util.HashMap;

/**
 * Created by James Park
 * email: jim@linuxnetworks.co.uk
 * Date: 25/1/2559.
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
    HashMap<String, Boolean> alerts = new HashMap<String, Boolean>();


    // Line properties
    float red = 1.0f;
    float prev_red = red;
    float l_width = 5.0f;


    public MyGLRenderer(int orientation) {
        super();
        this.orientation = orientation;
        Log.i(TAG, "Constructor orientation: " + this.orientation);

        // Initalise alerts to off
        alerts.put("mainLHWin", false);
        alerts.put("topLHWin",  false);
        alerts.put("LHStore",   false);
        alerts.put("mainRHWin", false);
        alerts.put("topRHWin",  false);
        alerts.put("backWin",   false);

        // Override GasStore alarm to ON
        alerts.put("gasStore",  true);
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

        // Set the camera position (View matrix)
        android.opengl.Matrix.setLookAtM(mViewMatrix, 0, 0, 0, 5f, 0f, 0f, 0f, 0f, 1.0f, 0.0f);

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
        mLHBody.draw(scratch, false);
        mRHBody.draw(scratch, false);
        mLHDoor.draw(scratch, false);
        mRHDoor.draw(scratch, false);
        mLHCab.draw(scratch, false);
        mRHCab.draw(scratch, false);
        mLHCabWin.draw(scratch, false);
        mRHCabWin.draw(scratch, false);
        mLHBotFlash.draw(scratch, false);
        mRHBotFlash.draw(scratch, false);
        mFrontWin.draw(scratch, false);

        // Alertable
        mLHMainWinO.draw(scratch, alerts.get("mainLHWin"));
        mLHMainWinI.draw(scratch, alerts.get("mainLHWin"));
        mLHTopWinI.draw(scratch, alerts.get("topLHWin"));
        mLHStoreO.draw(scratch, alerts.get("LHStore"));
        mLHStoreI.draw(scratch, alerts.get("LHStore"));
        mLHStoreCatch.draw(scratch, alerts.get("LHStore"));
        mRHMainWinO.draw(scratch, alerts.get("mainRHWin"));
        mRHMainWinI.draw(scratch, alerts.get("mainRHWin"));
        mRHTopWinI.draw(scratch, alerts.get("mainRHWin"));
        mRHGasStore.draw(scratch, alerts.get("gasStore"));
        mRHGasCatch.draw(scratch, alerts.get("gasStore"));
        mBackWinI.draw(scratch, alerts.get("backWin"));

       // Log.e(TAG, "onDrawFrame: called");

    }

    @Override
    public void onSurfaceChanged(GL10 gl, int width, int height) {
        GLES20.glViewport(0, 0, width, height);
        MyGLRenderer.checkGlError("glViewPort");

        float ratio = (float) width / height;
        // This projection Matrix is applied to object coordinates
        // in the onDrawFrame method.

//      ratio: 1.2949641 - Portrait
//      ratio: 1.9104477 - Landscape

        android.opengl.Matrix.frustumM(mProjectionMatrix, 0, (-ratio + 0.92f), (ratio - 0.92f), -0.5f, 0.5f, 4.19f, 7);
//      Log.i(TAG, "onSurfaceChanged: called");
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


