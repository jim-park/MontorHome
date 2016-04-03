package com.opengl_test.jim.opengl_test;

import android.app.Fragment;
import android.content.Intent;
import android.content.res.Configuration;
import android.opengl.GLSurfaceView;
import android.os.Bundle;
import android.app.Activity;
import android.os.Handler;
import android.support.v4.app.FragmentActivity;
import android.util.Log;

import android.support.v7.widget.Toolbar;
import android.support.design.widget.FloatingActionButton;
import android.support.design.widget.Snackbar;
import android.view.View;



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

public class MainActivity extends FragmentActivity {

    String TAG = "MainActivity";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        // TODO: Check device for a compatible Google Play services APK - here and in onResume()
        //       http://developer.android.com/google/play-services/setup.html

        // Start Services
        Intent regIntent = new Intent(this, RegistrationIntentService.class);
        try {
            startService(regIntent);
        } catch (Exception e) {
            Log.e(TAG, "Failed to start Service: " + e);
        }
/*
        start preferences view
        Intent i = new Intent(this, MyPreferencesActivity.class);
        startActivity(i);
*/
        // Set Content View ( calls fragments )
        setContentView(R.layout.activity_main);
    }

    @Override
    public void onConfigurationChanged(Configuration config) {
        Log.i(TAG, "onConfugurationChanged: Called");
        /*
        if (config.orientation == Configuration.ORIENTATION_LANDSCAPE) {
            setContentView(R.layout.activity_main_horiz);
        }
        */
        Log.i(TAG, "onConfugurationChanged: Exiting");
    }


/*
        setContentView(R.layout.activity_main);
        Toolbar toolbar = (Toolbar) findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);

        FloatingActionButton fab = (FloatingActionButton) findViewById(R.id.fab);
        fab.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Snackbar.make(view, "Replace with your own action", Snackbar.LENGTH_LONG)
                        .setAction("Action", null).show();
            }
        });
    }


/*
    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        // Inflate the menu; this adds items to the action bar if it is present.
        getMenuInflater().inflate(R.menu.menu_mainactivity, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        // Handle action bar item clicks here. The action bar will
        // automatically handle clicks on the Home/Up button, so long
        // as you specify a parent activity in AndroidManifest.xml.
        int id = item.getItemId();

        //noinspection SimplifiableIfStatement
        if (id == R.id.action_settings) {
            return true;
        }

        return super.onOptionsItemSelected(item);
    }
*/
}
