package com.opengl_test.jim.opengl_test;

import android.os.Bundle;
import android.util.Log;

import com.google.android.gms.gcm.GcmListenerService;

/**
 * Created by jim on 4/3/2559.
 */
public class MyGcmListenerService extends GcmListenerService {

    String TAG = "GcmListenerService";

    @Override
    public void onMessageReceived(String from, Bundle data) {
        String message = data.getString("data1");
        Log.d(TAG, "From: " + from);
        Log.d(TAG, "Message: " + message);

        if (message != null ) {
            if (message.matches("1")) {
                MyGLRenderer.setAlertMainLHWin(true);
                Log.d(TAG, "setMLHWin Alert: true");
            } else {
                MyGLRenderer.setAlertMainLHWin(false);
                Log.d(TAG, "setMLHWin Alert: false");
            }
        } else {
            Log.e(TAG, "Got null GCMessage");
        }
    }
}
