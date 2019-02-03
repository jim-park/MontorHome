package com.lnl.montorhome;

import android.content.Context;
import android.os.AsyncTask;
import android.util.Log;
import android.content.SharedPreferences;
import android.preference.PreferenceManager;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;

/**
 * Created by James Park on 28/01/19.
 */
public class FetchDataTask extends AsyncTask<String, Void, FetchDataTask.Wrapper> {

    String TAG = "FetchDataTask";

    class Wrapper
    {
        String data = "";
        String type = "";
    }
    private static final String API_URL0 = "http://188.30.45.248:21001/";
    private static final String API_URL1 = "http://192.168.8.98:21001/";
    private AsyncResponse delegate = null;
    private Context appContext;
    private Wrapper wrapper =new Wrapper();

    public FetchDataTask(MainActivity caller) {
        delegate = caller;
        appContext = caller.getApplicationContext();
    }

    public interface AsyncResponse {
        void processFinish(Wrapper output);
    }

    @Override
    protected void onPostExecute(Wrapper result) {
        delegate.processFinish(result);
    }

    @Override
    protected Wrapper doInBackground(String... params) {

        wrapper.type = params[0];
        HttpURLConnection urlConnection;
        URL url;
        SharedPreferences prefs = PreferenceManager.getDefaultSharedPreferences(appContext);

        try {
            // Retrieve API server address from preferences and build the url.
            url = new URL("http://" + prefs.getString("key_api_server_addr", "NOTFOUND") + ":21001/" + params[0]);
            Log.d("INFO", "Opening URL: " + url);
            urlConnection = (HttpURLConnection) url.openConnection();

            try {
                BufferedReader bufferReader = new BufferedReader(new InputStreamReader(urlConnection.getInputStream()));
                StringBuilder stringBuilder = new StringBuilder();
                String line;
                while((line = bufferReader.readLine()) != null) {
                    stringBuilder.append(line);
                }
                bufferReader.close();
                wrapper.data = stringBuilder.toString();
                return wrapper;
            }
            finally {
                urlConnection.disconnect();
            }
        }
        catch (Exception e) {
            Log.e("ERROR", e.getMessage());
            wrapper.data = "0.0";
            return wrapper;
        }

    }
}
