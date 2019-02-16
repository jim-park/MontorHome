package com.lnl.montorhome;

import android.app.Fragment;
import android.os.Bundle;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;

/**
 * Created by James Park
 * email: jim@linuxnetworks.co.uk
 * Date: 6/3/2559.
 */
public class BaseStatsFragment extends Fragment {

    String TAG = "BaseStatsFrag";

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container, Bundle savedInstanceState) {
        View view = inflater.inflate(R.layout.fragmentbasestats, container, false);
        Log.d(TAG, "onCreateView");
        return view;
    }

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        Log.d(TAG, "onCreate");
    }

}
