package com.lnl.montorhome;

import android.os.AsyncTask;
import android.util.Log;
import android.widget.TextView;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;

public class FetchBatteryCurrentTask extends AsyncTask<Void, Void, String> {

    private static final String API_URL = "http://192.168.8.102:5000/batt_voltage";
    private Exception exception;
    public AsyncResponse delegate = null;
    TextView responseView;

    public interface AsyncResponse {
        void processFinish(String output);
    }

    public FetchBatteryCurrentTask(AsyncResponse delegate){
        this.delegate = delegate;
    }

    @Override
    protected void onPostExecute(String result) {
        delegate.processFinish(result);
    }

    @Override
    protected String doInBackground(Void... urls) {

        try {
            URL url = new URL(API_URL);
            HttpURLConnection urlConnection = (HttpURLConnection) url.openConnection();
            try {
                BufferedReader bufferReader = new BufferedReader(new InputStreamReader(urlConnection.getInputStream()));
                StringBuilder stringBuilder = new StringBuilder();
                String line;
                while((line = bufferReader.readLine()) != null) {
                    Log.i("INFO", line);
                    stringBuilder.append(line);
                }
                bufferReader.close();
                return stringBuilder.toString();
            }
            finally {
                urlConnection.disconnect();
            }
        }
        catch (Exception e) {
            Log.e("ERROR", e.getMessage());
            return null;
        }

    }
}
