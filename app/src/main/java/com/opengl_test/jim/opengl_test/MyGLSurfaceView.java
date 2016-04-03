package com.opengl_test.jim.opengl_test;

import android.app.Activity;
import android.app.Notification;
import android.content.Context;
import android.opengl.GLSurfaceView;
import android.util.Log;
import android.view.Display;
import android.view.MotionEvent;
import android.view.WindowManager;

/**
 * Created by jim on 25/1/2559.
 */
public class MyGLSurfaceView extends GLSurfaceView {

    private final MyGLRenderer mRenderer;
    private final float TOUCH_SCALE_FACTOR = 180.0f / 320;
    private float mPreviousX;
    private float mPreviousY;
    private String TAG = "MYGLSurfaceView";

    public MyGLSurfaceView(Context context) {
        super(context);

        Display display = ((WindowManager) this.getContext().getSystemService(Context.WINDOW_SERVICE)).getDefaultDisplay();
        int orientation = display.getRotation();

        Log.i(TAG, "ORIENTATION: " + orientation);

        // Create an Open GL ES 2.0 Context.
        setEGLContextClientVersion(2);

        // Set the Renderer for drawing on the GLSurfaceView
        mRenderer = new MyGLRenderer(orientation);
        setRenderer(mRenderer);

        // Render the view only when there is a change in the drawing data
        // Might want continuious render for colour changes
        // setRenderMode(GLSurfaceView.RENDERMODE_WHEN_DIRTY);

    }

    @Override
    public boolean onTouchEvent(MotionEvent e) {
        // MotionEvent reports input details from the touch screen
        // and other input controls. In this case you are only
        // interested in events where the touch position changed.

        float x = e.getX();
        float y = e.getY();

        switch (e.getAction()) {
            case (MotionEvent.ACTION_MOVE):

                float dx = x - mPreviousX;
                float dy = y - mPreviousY;

                // Reverse direction of rotation above the mid line
                if (y > getHeight() / 2) {
                    dx = dx * -1;
                }

                // Reverse direction of rotation to left of the mid line
                if ( x > getWidth() / 2 ) {
                    dy = dy * -1;
                }

                mRenderer.setAngle(
                        mRenderer.getAngle() + ((dx + dy) * TOUCH_SCALE_FACTOR)

                );
                requestRender();
        };
        mPreviousX = x;
        mPreviousY = y;

        return true;
    }
}
