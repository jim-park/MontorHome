package com.opengl_test.jim.opengl_test;

import android.app.Fragment;
import android.app.FragmentTransaction;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.res.Configuration;
import android.location.GpsStatus;
import android.os.Bundle;
import android.preference.PreferenceManager;
import android.support.v4.app.FragmentActivity;
import android.support.v7.app.ActionBarActivity;
import android.support.v7.app.AppCompatActivity;
import android.util.Log;

import android.support.v7.widget.Toolbar;
import android.view.Menu;
import android.view.MenuInflater;
import android.view.MenuItem;

import java.util.prefs.Preferences;



/*
import android.opengl.GLES20;
import android.os.Handler;
import android.util.Log;
import android.view.Menu;
import android.view.MenuItem;
import android.content.Context;

import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.nio.FloatBuffer;


*/
// Server API Key
// AIzaSyCP55eg2J2ZPhexPHcHyNKXpDUDTWakAvY
//
// Sender ID (Project number)
// 162524205106

public class MainActivity extends AppCompatActivity {

    String TAG = "MainActivity";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        Log.i(TAG, "Created");


        // TODO: Check device for a compatible Google Play services APK - here and in onResume()
        //       http://developer.android.com/google/play-services/setup.html

        // Start GCM Registration Service
        Intent regIntent = new Intent(this, RegistrationIntentService.class);
        try {
            startService(regIntent);
        } catch (Exception e) {
            Log.e(TAG, "Failed to start GCM Reg Service: " + e.toString());
        }


        // Set Content View ( calls fragments )
        setContentView(R.layout.activity_main);

        // Setup Preference Change Listener
        try {
            SharedPreferences prefs = PreferenceManager.getDefaultSharedPreferences(this);
            SharedPreferences.OnSharedPreferenceChangeListener listener = new PreferenceChangeListener();
            prefs.registerOnSharedPreferenceChangeListener(listener);
            Log.i(TAG, "Started preferences change listener." + listener.toString());
            Log.i(TAG, "app_server_addr: " + prefs.getString("key_app_server_addr", "key not found"));
        } catch(Exception e) {
            Log.e(TAG, "Failed to start preferences change listener. e: " + e.toString());
        }

        // Setup Action Bar
        Toolbar toolbar = (Toolbar) findViewById(R.id.my_toolbar);
        setSupportActionBar(toolbar);

    }

    // Deal with a change in orientation
    @Override
    public void onConfigurationChanged(Configuration config) {
        super.onConfigurationChanged(config);
        Log.i(TAG, "onConfugurationChanged: Called");

        final Fragment fragmentBSV = getFragmentManager().findFragmentById(R.id.basestatsView);
        FragmentTransaction ft = getFragmentManager().beginTransaction();

        if (config.orientation == Configuration.ORIENTATION_LANDSCAPE) {
            // Hide the Base Stats View and Action Bar
            ft.hide(fragmentBSV);
            ft.commit();
            getSupportActionBar().hide();
        } else {
            // Show the Base Stats View and Action Bar
            ft.show(fragmentBSV);
            ft.commit();
            getSupportActionBar().show();
        }
        Log.i(TAG, "onConfugurationChanged: Exiting");
    }


    /*
     * Options Menu Setup
     */
    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        MenuInflater inflater = getMenuInflater();
        // Inflate the menu; this adds items to the action bar if it is present.
        inflater.inflate(R.menu.menu_mainactivity, menu);
        return true;
    }

    // Deal with options selected
    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        // Handle item selection
        switch (item.getItemId()) {
            case R.id.action_settings:
                Intent prefs = new Intent(this, SettingsActivity.class);
                startActivity(prefs);
                return true;
            default:
                return super.onOptionsItemSelected(item);
        }
    }

    // Wrapper for SharedPreferences.OnSharedPreferenceChangeListener
    private class PreferenceChangeListener implements SharedPreferences.OnSharedPreferenceChangeListener {

        @Override
        public void onSharedPreferenceChanged(SharedPreferences sharedPreferences, String key) {
            Log.i(TAG, "onSharedPreferenceChanged called, key: " + key);

            if (key.equals("key_app_server_addr")) {
                Log.i(TAG, "key_app_server_addr: " + key);
            }
        }
    }
}
