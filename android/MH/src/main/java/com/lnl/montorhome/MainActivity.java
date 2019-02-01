package com.lnl.montorhome;

import android.app.Fragment;
import android.app.FragmentTransaction;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.res.Configuration;
import android.os.Bundle;
import android.preference.PreferenceManager;
import android.support.v7.app.AppCompatActivity;
import android.util.Log;
import android.support.v7.widget.Toolbar;
import android.view.Menu;
import android.view.MenuInflater;
import android.view.MenuItem;
import android.widget.TextView;
import com.lnl.montorhome.FetchDataTask.AsyncResponse;

public class MainActivity extends AppCompatActivity implements AsyncResponse {
    String TAG = "MainActivity";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        /*
         * TODO: Check device for a compatible Google Play services APK - here and in onResume()
         *       http://developer.android.com/google/play-services/setup.html
         */

        // Set Content View
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

        /*
        /   Fetch Battery related data
        */
        // Battery Voltage
        FetchDataTask fetchBattVoltageTask =new FetchDataTask(this);
        fetchBattVoltageTask.execute("batt_voltage");

        // Battery Current
        FetchDataTask fetchBattCurrTask =new FetchDataTask(this);
        fetchBattCurrTask.execute("batt_current");

        // Battery Temperature
        FetchDataTask fetchBattTempTask =new FetchDataTask(this);
        fetchBattTempTask.execute("batt_temp");

        /*
         * Fetch PV related data
         */
        // PV Voltage
        FetchDataTask fetchPVVoltageTask =new FetchDataTask(this);
        fetchPVVoltageTask.execute("pv_voltage");

        // PV Current
        FetchDataTask fetchPVCurrentTask =new FetchDataTask(this);
        fetchPVCurrentTask.execute("pv_current");

        // PV Power
        FetchDataTask fetchPVPowerTask =new FetchDataTask(this);
        fetchPVPowerTask.execute("pv_power");

        /*
         * Fetch load related data
         */
        // Load Voltage
        FetchDataTask fetchLoadVoltageTask =new FetchDataTask(this);
        fetchLoadVoltageTask.execute("load_voltage");

        // Load Current
        FetchDataTask fetchLoadCurrentTask =new FetchDataTask(this);
        fetchLoadCurrentTask.execute("load_current");

        // Load Power
        FetchDataTask fetchLoadPowerTask =new FetchDataTask(this);
        fetchLoadPowerTask.execute("load_power");
    }

    /*
     * This overrides the implemented method from FetchDataTask
     */
    @Override
    public void processFinish(FetchDataTask.Wrapper output){
        //Receive the result fired from FetchDataTask class
        //of onPostExecute(result) method.
        Log.d("INFO", "data: " + output.data + ", type: " + output.type);
        TextView dataViewId = null;

        switch(output.type) {
            case "batt_voltage":
                dataViewId = (TextView) findViewById(R.id.batt_voltage);
                break;
            case "batt_current":
                dataViewId = (TextView) findViewById(R.id.batt_current);
                break;
            case "pv_voltage":
                dataViewId = (TextView) findViewById(R.id.pv_voltage);
                break;
            case "pv_current":
                dataViewId = (TextView) findViewById(R.id.pv_current);
                break;
            case "pv_power":
                dataViewId = (TextView) findViewById(R.id.pv_power);
                break;
            case "load_voltage":
                dataViewId = (TextView) findViewById(R.id.load_voltage);
                break;
            case "load_current":
                dataViewId = (TextView) findViewById(R.id.load_current);
                break;
            case "load_power":
                dataViewId = (TextView) findViewById(R.id.load_power);
                break;
        }
        if(dataViewId != null) {
            dataViewId.setText(output.data);
        }
    }


    /*
     * Deal with a change in orientation
     */
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

    /*
     * Options Menu - Deal with options selected
     */
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

    /*
     * Wrapper for SharedPreferences.OnSharedPreferenceChangeListener
     */
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