package com.lnl.montorhome;

import android.app.Fragment;
import android.app.FragmentTransaction;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.res.Configuration;
import android.os.Bundle;
import android.preference.PreferenceManager;
import android.support.v7.app.AppCompatActivity;
import android.support.v7.widget.Toolbar;
import android.util.Log;
import android.view.Menu;
import android.view.MenuInflater;
import android.view.MenuItem;
import android.view.View;
import android.widget.Button;
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

        // Setup Preferences and Preference Change Listener
        SharedPreferences prefs = PreferenceManager.getDefaultSharedPreferences(this.getApplicationContext());

        // Setup Action Bar
        Toolbar toolbar = (Toolbar) findViewById(R.id.my_toolbar);
        setSupportActionBar(toolbar);

        /*
        /   Initialise data display - fetch and display remote instrumentation data
        */
        for (String dataCode : dataCodes.allData) {
            // Create and exeute a new AsyncTask for each request.
            FetchDataTask fetchfromAPITask =new FetchDataTask(MainActivity.this);
            fetchfromAPITask.execute(dataCode);
        }
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
            case dataCodes.battVoltage:
                dataViewId = (TextView) findViewById(R.id.batt_voltage);
                break;
            case dataCodes.battCurrent:
                dataViewId = (TextView) findViewById(R.id.batt_current);
                break;
            case dataCodes.battTemp:
                dataViewId = (TextView) findViewById(R.id.batt_temp);
                break;
            case dataCodes.pvVoltage:
                dataViewId = (TextView) findViewById(R.id.pv_voltage);
                break;
            case dataCodes.pvCurrent:
                dataViewId = (TextView) findViewById(R.id.pv_current);
                break;
            case dataCodes.pvPower:
                dataViewId = (TextView) findViewById(R.id.pv_power);
                break;
            case dataCodes.loadVoltage:
                dataViewId = (TextView) findViewById(R.id.load_voltage);
                break;
            case dataCodes.loadCurrent:
                dataViewId = (TextView) findViewById(R.id.load_current);
                break;
            case dataCodes.loadPower:
                dataViewId = (TextView) findViewById(R.id.load_power);
                break;
        }
        if(dataViewId != null) {
            // Format output string to 2dp
            dataViewId.setText( String.format("%.2f", Float.parseFloat(output.data)) );
        }


        /*
            Refresh button listener
         */
        Button button = (Button) findViewById(R.id.refresh_button);
        button.setOnClickListener(new View.OnClickListener() {
        public void onClick(View v) {
                //   Fetch and display remote instrumentation data
                for (String dataCode : dataCodes.allData) {
                    // Create and exeute a new AsyncTask for each request.
                    FetchDataTask fetchfromAPITask =new FetchDataTask(MainActivity.this);
                    fetchfromAPITask.execute(dataCode);
                }
            }
        });
    }

    /*
     * Static data structure for names of api call parameters
     */
    public final static class dataCodes {
        final static String battVoltage = "batt_voltage";
        final static String battCurrent = "batt_current";
        final static String battTemp = "batt_temperature";
        final static String pvVoltage = "pv_voltage";
        final static String pvCurrent = "pv_current";
        final static String pvPower = "pv_power";
        final static String loadVoltage = "load_voltage";
        final static String loadCurrent = "load_current";
        final static String loadPower = "load_power";

        final static String[] allData = {dataCodes.battVoltage, dataCodes.battCurrent, dataCodes.battTemp,
                dataCodes.pvVoltage, dataCodes.pvCurrent, dataCodes.pvPower,
                dataCodes.loadVoltage, dataCodes.loadCurrent, dataCodes.loadPower};
    }

    /*
     * Deal with a change in orientation
     */
    @Override
    public void onConfigurationChanged(Configuration config) {
        super.onConfigurationChanged(config);

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
                Intent prefs = new Intent(this.getApplicationContext(), SettingsActivity.class);
                startActivity(prefs);
                return true;
            default:
                return super.onOptionsItemSelected(item);
        }
    }
}