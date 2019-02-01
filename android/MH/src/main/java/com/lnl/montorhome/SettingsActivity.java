package com.lnl.montorhome;

import android.app.Activity;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.preference.PreferenceManager;
import android.util.Log;

/**
 * Created by jim on 08/04/16.
 */
public class SettingsActivity extends Activity {

    private static final String TAG = "SettingsActivity";
    public static final String KEY_PREF_APP_SERVER= "app_server_addr";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        Log.i(TAG, "onCreate called");
        // Display the fragment as the main content.
        getFragmentManager().beginTransaction()
                .replace(android.R.id.content, new SettingsFragment())
                .commit();

        // Setup Preference Change Listener
        SharedPreferences prefs = PreferenceManager.getDefaultSharedPreferences(this);
        SharedPreferences.OnSharedPreferenceChangeListener listener = new PreferenceChangeListener();
        prefs.registerOnSharedPreferenceChangeListener(listener);
        Log.i(TAG, "app_server_addr: " + prefs.getString("key_app_server_addr", "key not found"));

    }

    // Wrapper for SharedPreferences.OnSharedPreferenceChangeListener
    private class PreferenceChangeListener implements SharedPreferences.OnSharedPreferenceChangeListener {

        @Override
        public void onSharedPreferenceChanged(SharedPreferences sharedPreferences, String key) {
            Log.i(TAG, "onSharedPreferenceChanged called, key: " + key);

            if (key.equals("app_server_addr")) {
                Log.i(TAG, "app_server_addr: " + key);
            }
        }
    }
}
