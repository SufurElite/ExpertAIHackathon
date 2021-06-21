package com.Sufur.datinganalyst;

import android.annotation.SuppressLint;
import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.media.projection.MediaProjectionManager;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;

import com.google.firebase.auth.FirebaseAuth;
import com.google.firebase.firestore.FirebaseFirestore;
import com.google.firebase.storage.FirebaseStorage;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class ChatActivity extends AppCompatActivity {
    private TextView textView;
    private TextView resultText;
    private Button launchButton;
    private Button postDebugBtn;
    private Button getDebugBtn;
    private ApiInterface apiInterface;
    private static final int REQUEST_CODE = 100;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.signedin_activity);
        textView = findViewById(R.id.viewEmail);
        textView.setText(Common.currentUser.getEmail());
        resultText = findViewById(R.id.text1);
        launchButton = findViewById(R.id.createChatHead);
        Common.db = FirebaseStorage.getInstance("gs://chadvice.appspot.com");
        apiInterface = ApiClient.getApiClient('s').create(ApiInterface.class);
        postDebugBtn = findViewById(R.id.postFromServer);
        getDebugBtn = findViewById(R.id.getFromServer);
        initializeView();
    }

    @SuppressLint("MissingSuperCall")
    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        if (requestCode == REQUEST_CODE) {
            if (resultCode == Activity.RESULT_OK) {
                startService(com.Sufur.datinganalyst.ScreenCaptureService.getStartIntent(this, resultCode, data));
            }
        }
    }

    /**
     * Set and initialize the view elements.
     */
    private void initializeView() {
        launchButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                if(!Common.analysis) {
                    // Start Projection
                    startProjection();
                    // Launch Chathead
                    startService(new Intent(ChatActivity.this, ChatHeadService.class));
                    launchButton.setText(R.string.stop_analysis);
                    Common.analysis = true;
                } else {
                    // Stop Projection
                    stopProjection();
                    launchButton.setText(R.string.launch_btn);
                    Common.analysis = false;
                }
            }
        });

        findViewById(R.id.logout_btn).setOnClickListener(new View.OnClickListener(){
            @Override
            public void onClick(View view){
                FirebaseAuth.getInstance().signOut();
                Common.currentUser = null;
                startActivity(new Intent(ChatActivity.this, MainActivity.class));
                finish();
            }
        });

        postDebugBtn.setOnClickListener(new View.OnClickListener(){
            @Override
            public void onClick(View v) {

            }
        });

        getDebugBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Call<String> call = apiInterface.getApiResponse(Common.currentUser.getEmail());
                call.enqueue(new Callback<String>() {
                    @Override
                    public void onResponse(@NonNull Call<String> call, @NonNull Response<String> response) {
                        String res = response.body().toString();
                        resultText.setText(res);
                    }

                    @Override
                    public void onFailure(@NonNull Call<String> call, @NonNull Throwable t) {
                        resultText.setText("Failure to communicate");
                        Log.e("Communication",t.getMessage());
                    }
                });
            }
        });
    }

    /****************************************** UI Widget Callbacks *******************************/
    private void startProjection() {
        MediaProjectionManager mProjectionManager =
                (MediaProjectionManager) getSystemService(Context.MEDIA_PROJECTION_SERVICE);
        startActivityForResult(mProjectionManager.createScreenCaptureIntent(), REQUEST_CODE);
    }

    private void stopProjection() {
        startService(com.Sufur.datinganalyst.ScreenCaptureService.getStopIntent(this));
    }

    @Override
    public void onDestroy()
    {
        // Make sure to stop recording if the app is closed
        stopProjection();
        super.onDestroy();
    }
}
