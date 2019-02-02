package com.lnl.montorhome;

import android.os.Bundle;
import android.preference.PreferenceFragment;
import android.util.Log;

/**
 * Created by jim on 03/04/16.
 */
public class SettingsFragment extends PreferenceFragment {

    String TAG = "SettingsFragment";

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        Log.d(TAG, "onCreeate called");
        // Load the preferences from an XML resource
        addPreferencesFromResource(R.xml.preferences);

//        getFragmentManager().beginTransaction().replace(android.R.id.content, new SettingsFragment()).commit();
    }

    /*
    public static class MyPreferenceFragment extends PreferenceFragment {

        @Override
        public void onCreate(Bundle savedInstanceState) {
            super.onCreate(savedInstanceState);
            addPreferencesFromResource(R.xml.preferences);
        }
    }
    */
}
