package com.lnl.montorhome;

import android.app.Activity;
import android.os.Bundle;
import android.util.Log;
import android.widget.TextView;
import com.lnl.montorhome.FetchDataTask.AsyncResponse;

import java.util.Locale;

/**
 * Created by James Park
 * email: jim@linuxnetworks.co.uk
 * Date: 17/02/19.
 */

public class BatteryStatsActivity extends Activity implements AsyncResponse{

    private static final String TAG = "BatteryStatsActivity";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.batterystats);

        final String[] stats = {"batt_soc", "batt_voltage_max", "batt_voltage_min"};

        for (String stat : stats) {
            // Create and exeute a new AsyncTask for each request.
            FetchDataTask fetchfromAPITask = new FetchDataTask(this.getApplicationContext(), BatteryStatsActivity.this);
            fetchfromAPITask.execute(stat);
        }
    }


    /*
     * This overrides the implemented method from FetchDataTask
     */
    @Override
    public void processFinish(FetchDataTask.Wrapper output) {
        //Receive the result fired from FetchDataTask class
        //of onPostExecute(result) method.
        Log.d(TAG, "data: " + output.data + ", type: " + output.type);
        TextView dataViewId = null;

        switch(output.type) {
            case "batt_soc":
                dataViewId = (TextView) findViewById(R.id.battery_soc_value);
                break;
            case "batt_voltage_max":
                dataViewId = (TextView) findViewById(R.id.battery_max_voltage_today_value);
                break;
            case "batt_voltage_min":
                dataViewId = (TextView) findViewById(R.id.battery_min_voltage_today_value);
                break;
        }
        if(dataViewId != null) {
        // Format output string to 2dp
        dataViewId.setText(String.format(Locale.getDefault(), "%.2f", Float.parseFloat(output.data)) );
    }
    }
}
