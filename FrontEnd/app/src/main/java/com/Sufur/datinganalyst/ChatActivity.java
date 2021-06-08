package com.Sufur.datinganalyst;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.view.View;

import com.google.firebase.auth.FirebaseAuth;

import androidx.appcompat.app.AppCompatActivity;

public class ChatActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.signedin_activity);
        initializeView();
    }
    /**
     * Set and initialize the view elements.
     */
    private void initializeView() {
        findViewById(R.id.createChatHead).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                startService(new Intent(ChatActivity.this, ChatHeadService.class));
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
    }
}
