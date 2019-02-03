package com.lnl.montorhome;

import android.app.Activity;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.preference.PreferenceManager;
import android.util.Log;

/**
 * Created by James Park on 08/04/16.
 */
public class SettingsActivity extends Activity {

    private static final String TAG = "SettingsActivity";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        // Display the fragment as the main content.
        getFragmentManager().beginTransaction()
                .replace(android.R.id.content, new SettingsFragment())
                .commit();

        // Setup Preferences Change Listener
        SharedPreferences prefs = PreferenceManager.getDefaultSharedPreferences(this.getApplicationContext());
        SharedPreferences.OnSharedPreferenceChangeListener listener = new PreferenceChangeListener();
        prefs.registerOnSharedPreferenceChangeListener(listener);
    }

    // Wrapper for SharedPreferences.OnSharedPreferenceChangeListener
    public class PreferenceChangeListener implements SharedPreferences.OnSharedPreferenceChangeListener {

        @Override
        public void onSharedPreferenceChanged(SharedPreferences sharedPreferences, String key) {
            Log.i(TAG, "PreferenceChanged " + key + " changed to " + sharedPreferences.getString(key, "NOTFOUND"));
        }
    }
}
