package com.lnl.montorhome;

/**
 * Created by James Park
 * email: jim@linuxnetworks.co.uk
 * Date: 28/2/2559.
 */

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.net.ConnectivityManager;
import android.net.NetworkInfo;
import android.preference.PreferenceManager;
import android.util.Log;

public class NetworkChangeBroadcastReceiver extends BroadcastReceiver {
    String TAG = "BcastRcvr";
    public static Boolean connected = false;

    @Override
    public void onReceive(Context context, Intent intent) {

        // Retreive the system WLAN name from preferences.
        SharedPreferences prefs = PreferenceManager.getDefaultSharedPreferences(context.getApplicationContext());
        String desired_wlan_ssid = prefs.getString("wlan_ssid", "WLAN NOT SET");

        // Retreive parcelled NetworkInfo object.
        NetworkInfo netInfo = intent.getParcelableExtra("networkInfo");

        // Extract the data we require.
        int netType = netInfo.getType();
        String netSSID = netInfo.getExtraInfo().replace("\"", "");
        NetworkInfo.State netState = netInfo.getState();

        Log.d(TAG, "netState: " + netState);
        Log.d(TAG, "netSSID: " + netSSID);
        Log.d(TAG, "netType: " + netType);

        // Test if we are connected to our system WLAN.
        connected = netType == ConnectivityManager.TYPE_WIFI
                && netState == NetworkInfo.State.CONNECTED
                && netSSID.equals(desired_wlan_ssid);
        Log.d(TAG, "Wifi connected: " + connected);
    }

    public static boolean connectedToSystemLAN() {
        return connected;
    }

}
