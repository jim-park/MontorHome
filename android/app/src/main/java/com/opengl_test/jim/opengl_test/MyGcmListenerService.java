package com.opengl_test.jim.opengl_test;

import android.os.Bundle;
import android.util.Log;
import android.widget.TextView;

import com.google.android.gms.gcm.GcmListenerService;

import static android.app.PendingIntent.getActivity;

/**
 * Created by jim on 4/3/2559.
 */
public class MyGcmListenerService extends GcmListenerService {

    String TAG = "GcmListenerService";

    @Override
    public void onMessageReceived(String from, Bundle data) {
        String message = data.getString("batt1");
        Log.d(TAG, "From: " + from);
        Log.d(TAG, "Message: " + message);

        if (message != null ) {
            Log.d(TAG, "Got Batt 1 Voltage: " + message);

        } else {
            Log.e(TAG, "No Batt 1 Voltage Found");
        }
    }
}
