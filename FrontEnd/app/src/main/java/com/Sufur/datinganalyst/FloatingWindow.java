package com.Sufur.datinganalyst;

import android.app.Service;
import android.content.Context;
import android.content.Intent;
import android.graphics.PixelFormat;
import android.os.Build;
import android.os.IBinder;
import android.text.Editable;
import android.text.TextWatcher;
import android.util.DisplayMetrics;
import android.util.Log;
import android.view.Gravity;
import android.view.LayoutInflater;
import android.view.MotionEvent;
import android.view.View;
import android.view.ViewGroup;
import android.view.WindowManager;
import android.view.inputmethod.InputMethodManager;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

import com.Sufur.datinganalyst.Common;

public class FloatingWindow extends Service {

    // The reference variables for the
    // ViewGroup, WindowManager.LayoutParams,
    // WindowManager, Button, EditText classes are created
    private ViewGroup floatView;
    private int LAYOUT_TYPE;
    private WindowManager.LayoutParams floatWindowLayoutParam;
    private WindowManager windowManager;
    private Button closeBtn;
    private EditText inputArea;
    private Button saveBtn;
    private ApiInterface apiInterface;
    // As FloatingWindowGFG inherits Service class,
    // it actually overrides the onBind method
    @Nullable
    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }
    //private TextView featureText;
    @Override
    public void onCreate() {
        super.onCreate();
        // The screen height and width are calculated, cause
        // the height and width of the floating window is set depending on this
        int width = Common.displayWidth;
        int height = Common.displayHeight;

        // To obtain a WindowManager of a different Display,
        // we need a Context for that display, so WINDOW_SERVICE is used
        windowManager = (WindowManager) getSystemService(WINDOW_SERVICE);

        // A LayoutInflater instance is created to retrieve the
        // LayoutInflater for the floating_layout xml
        LayoutInflater inflater = (LayoutInflater) getBaseContext().getSystemService(LAYOUT_INFLATER_SERVICE);

        // inflate a new view hierarchy from the floating_layout xml
        floatView = (ViewGroup) inflater.inflate(R.layout.floating_layout, null);

        // The Buttons and the EditText are connected with
        // the corresponding component id used in floating_layout xml file
        closeBtn = floatView.findViewById(R.id.chatActivityCloseButton);
        inputArea = floatView.findViewById(R.id.inputText);
        saveBtn = floatView.findViewById(R.id.saveBtn);

        updateStats();

        // Just like MainActivity, the text written
        // in Maximized will stay
        inputArea.setText(Common.currentInput);
        inputArea.setSelection(inputArea.getText().toString().length());
        inputArea.setCursorVisible(false);

        /*
        featureText= floatView.findViewById(R.id.conversationText);
        if(Common.textFromConvo!=""){
            featureText.setText(Common.textFromConvo.replace("<br/>","\n"));
        }*/

        // WindowManager.LayoutParams takes a lot of parameters to set the
        // the parameters of the layout. One of them is Layout_type.
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            // If API Level is more than 26, we need TYPE_APPLICATION_OVERLAY
            LAYOUT_TYPE = WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY;
        } else {
            // If API Level is lesser than 26, then we can
            // use TYPE_SYSTEM_ERROR,
            // TYPE_SYSTEM_OVERLAY, TYPE_PHONE, TYPE_PRIORITY_PHONE.
            // But these are all
            // deprecated in API 26 and later. Here TYPE_TOAST works best.
            LAYOUT_TYPE = WindowManager.LayoutParams.TYPE_TOAST;
        }

        // Now the Parameter of the floating-window layout is set.
        // 1) The Width of the window will be 55% of the phone width.
        // 2) The Height of the window will be 58% of the phone height.
        // 3) Layout_Type is already set.
        // 4) Next Parameter is Window_Flag. Here FLAG_NOT_FOCUSABLE is used. But
        // problem with this flag is key inputs can't be given to the EditText.
        // This problem is solved later.
        // 5) Next parameter is Layout_Format. System chooses a format that supports
        // translucency by PixelFormat.TRANSLUCENT
        floatWindowLayoutParam = new WindowManager.LayoutParams(
                (int) (width * (0.758f)),
                (int) (height * (0.80f)),
                LAYOUT_TYPE,
                WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE,
                PixelFormat.TRANSLUCENT
        );

        // The Gravity of the Floating Window is set.
        // The Window will appear in the center of the screen
        floatWindowLayoutParam.gravity = Gravity.CENTER;

        // X and Y value of the window is set
        floatWindowLayoutParam.x = 0;
        floatWindowLayoutParam.y = 0;

        // The ViewGroup that inflates the floating_layout.xml is
        // added to the WindowManager with all the parameters
        windowManager.addView(floatView, floatWindowLayoutParam);

        // The button that helps to minimise the app
        closeBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                // stopSelf() method is used to stop the service if
                // it was previously started
                stopSelf();
                Common.floatingRunning = false;

                // The window is removed from the screen
                windowManager.removeView(floatView);

                // The app will maximize again. So the MainActivity
                // class will be called again.
                //Intent backToHome = new Intent(FloatingWindow.this, MainActivity.class);

                // 1) FLAG_ACTIVITY_NEW_TASK flag helps activity to start a new task on the history stack.
                // If a task is already running like the floating window service, a new activity will not be started.
                // Instead the task will be brought back to the front just like the MainActivity here
                // 2) FLAG_ACTIVITY_CLEAR_TASK can be used in the conjunction with FLAG_ACTIVITY_NEW_TASK. This flag will
                // kill the existing task first and then new activity is started.
                //backToHome.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TASK);
                //startActivity(backToHome);
                Intent intent = new Intent(FloatingWindow.this, ChatHeadService.class);
                intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                startService(intent);
            }
        });

        // The EditText string will be stored
        // in currentDesc while writing
        inputArea.addTextChangedListener(new TextWatcher() {
            @Override
            public void beforeTextChanged(CharSequence charSequence, int i, int i1, int i2) {
                // Not Necessary
            }

            @Override
            public void onTextChanged(CharSequence charSequence, int i, int i1, int i2) {
                Common.currentInput = inputArea.getText().toString();
            }

            @Override
            public void afterTextChanged(Editable editable) {
                // Not Necessary
            }
        });

        // Another feature of the floating window is, the window is movable.
        // The window can be moved at any position on the screen.
        floatView.setOnTouchListener(new View.OnTouchListener() {
            final WindowManager.LayoutParams floatWindowLayoutUpdateParam = floatWindowLayoutParam;
            double x;
            double y;
            double px;
            double py;

            @Override
            public boolean onTouch(View v, MotionEvent event) {

                switch (event.getAction()) {
                    // When the window will be touched,
                    // the x and y position of that position
                    // will be retrieved
                    case MotionEvent.ACTION_DOWN:
                        x = floatWindowLayoutUpdateParam.x;
                        y = floatWindowLayoutUpdateParam.y;

                        // returns the original raw X
                        // coordinate of this event
                        px = event.getRawX();

                        // returns the original raw Y
                        // coordinate of this event
                        py = event.getRawY();
                        break;
                    // When the window will be dragged around,
                    // it will update the x, y of the Window Layout Parameter
                    case MotionEvent.ACTION_MOVE:
                        floatWindowLayoutUpdateParam.x = (int) ((x + event.getRawX()) - px);
                        floatWindowLayoutUpdateParam.y = (int) ((y + event.getRawY()) - py);

                        // updated parameter is applied to the WindowManager
                        windowManager.updateViewLayout(floatView, floatWindowLayoutUpdateParam);
                        break;
                }
                return false;
            }
        });

        // Floating Window Layout Flag is set to FLAG_NOT_FOCUSABLE,
        // so no input is possible to the EditText. But that's a problem.
        // So, the problem is solved here. The Layout Flag is
        // changed when the EditText is touched.
        inputArea.setOnTouchListener(new View.OnTouchListener() {
            @Override
            public boolean onTouch(View v, MotionEvent event) {
                inputArea.setCursorVisible(true);
                WindowManager.LayoutParams floatWindowLayoutParamUpdateFlag = floatWindowLayoutParam;
                // Layout Flag is changed to FLAG_NOT_TOUCH_MODAL which
                // helps to take inputs inside floating window, but
                // while in EditText the back button won't work and
                // FLAG_LAYOUT_IN_SCREEN flag helps to keep the window
                // always over the keyboard
                floatWindowLayoutParamUpdateFlag.flags = WindowManager.LayoutParams.FLAG_NOT_TOUCH_MODAL | WindowManager.LayoutParams.FLAG_LAYOUT_IN_SCREEN;

                // WindowManager is updated with the Updated Parameters
                windowManager.updateViewLayout(floatView, floatWindowLayoutParamUpdateFlag);
                return false;
            }
        });


        saveBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                // saves the text in savedInput variable
                Common.savedInput = inputArea.getText().toString();
                inputArea.setCursorVisible(false);
                WindowManager.LayoutParams floatWindowLayoutParamUpdateFlag = floatWindowLayoutParam;
                floatWindowLayoutParamUpdateFlag.flags = WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE;

                // The Layout Flag is changed back to FLAG_NOT_FOCUSABLE. and the Layout is updated with new Flag
                windowManager.updateViewLayout(floatView, floatWindowLayoutParamUpdateFlag);

                // INPUT_METHOD_SERVICE with Context is used
                // to retrieve a InputMethodManager for
                // accessing input methods which is the soft keyboard here
                InputMethodManager inputMethodManager = (InputMethodManager) getSystemService(Context.INPUT_METHOD_SERVICE);

                // The soft keyboard slides back in
                inputMethodManager.hideSoftInputFromWindow(floatView.getApplicationWindowToken(), 0);

                apiInterface = ApiClient.getApiClient('s').create(ApiInterface.class);
                TextView titleText = floatView.findViewById(R.id.titleText);
                titleText.setText(R.string.analysis_loading);
                Log.e("Potential Analysis", "Starting /potentialMessage/");
                Call<String> call = apiInterface.potentialMessage(Common.bitmapName,Common.savedInput);
                call.enqueue(new Callback<String>() {
                    @Override
                    public void onResponse(@NonNull Call<String> call, @NonNull Response<String> response) {
                        String res = response.body();
                        Log.e("Potential Analysis","Submitted Correctly "+response.isSuccessful());
                        if(res!=""){
                            Common.inquisitiveness = Integer.parseInt(res.substring(0, 1));
                            Common.interestingness = Integer.parseInt(res.substring(1, 2));
                            Common.ghostedness = Integer.parseInt(res.substring(2, 3));
                            Log.e("Potential Analysis", Integer.toString(Common.inquisitiveness)+" "+Integer.toString(Common.interestingness)+" "+Integer.toString(Common.ghostedness));
                            updateStats();
                        } else {
                            Log.e("Potential Analysis", "No conversation found to analyse");
                            Common.inquisitiveness = -1;
                            Common.interestingness = -1;
                            Common.ghostedness = -1;
                        }
                    }

                    @Override
                    public void onFailure(@NonNull Call<String> call, @NonNull Throwable t) {
                        Log.e("Communication",t.getMessage());
                    }
                });
            }
        });
    }

    private void updateStats(){
        TextView titleText = floatView.findViewById(R.id.titleText);
        // If there's any value, we know the analysis has loaded otherwise it's still loading
        if(Common.inquisitiveness>=1){
            titleText.setText(R.string.loaded_analysis);
        } else {
            titleText.setText(R.string.analysis_loading);
        }
        // Set inquisitive images
        ImageView imageView = floatView.findViewById(R.id.inquisitiveMin);
        imageView.setImageResource(R.drawable.ic_mouthshut);
        imageView = floatView.findViewById(R.id.inquisitiveEmojiOne);
        if(Common.inquisitiveness==1){
            imageView.setImageResource(R.drawable.ic_fire);
        } else {
            imageView.setImageResource(R.drawable.ic_redcircle);
        }
        imageView = floatView.findViewById(R.id.inquisitiveEmojiTwo);
        if(Common.inquisitiveness==2){
            imageView.setImageResource(R.drawable.ic_fire);
        } else {
            imageView.setImageResource(R.drawable.ic_yellowcircle);
        }
        imageView = floatView.findViewById(R.id.inquisitiveEmojiThree);
        if(Common.inquisitiveness==3){
            imageView.setImageResource(R.drawable.ic_fire);
        } else {
            imageView.setImageResource(R.drawable.ic_yellowcircle);
        }
        imageView = floatView.findViewById(R.id.inquisitiveEmojiFour);
        if(Common.inquisitiveness==4){
            imageView.setImageResource(R.drawable.ic_fire);
        } else {
            imageView.setImageResource(R.drawable.ic_greencircle);
        }
        imageView = floatView.findViewById(R.id.inquisitiveMax);
        imageView.setImageResource(R.drawable.ic_think);

        imageView = floatView.findViewById(R.id.interestingMin);
        imageView.setImageResource(R.drawable.ic_sleep);
        imageView = floatView.findViewById(R.id.interestingEmojiOne);
        if(Common.interestingness==1){
            imageView.setImageResource(R.drawable.ic_fire);
        } else {
            imageView.setImageResource(R.drawable.ic_redcircle);
        }
        imageView = floatView.findViewById(R.id.interestingEmojiTwo);
        if(Common.interestingness==2){
            imageView.setImageResource(R.drawable.ic_fire);
        } else {
            imageView.setImageResource(R.drawable.ic_yellowcircle);
        }
        imageView = floatView.findViewById(R.id.interestingEmojiThree);
        if(Common.interestingness==3){
            imageView.setImageResource(R.drawable.ic_fire);
        } else {
            imageView.setImageResource(R.drawable.ic_yellowcircle);
        }
        imageView = floatView.findViewById(R.id.interestingEmojiFour);
        if(Common.interestingness==4){
            imageView.setImageResource(R.drawable.ic_fire);
        } else {
            imageView.setImageResource(R.drawable.ic_greencircle);
        }
        imageView = floatView.findViewById(R.id.interestingMax);
        imageView.setImageResource(R.drawable.ic_stareyes);
        imageView = floatView.findViewById(R.id.ghostedEmojiMin);
        imageView.setImageResource(R.drawable.ic_ghosted);
        imageView = floatView.findViewById(R.id.ghostedEmojiOne);
        if(Common.ghostedness==1){
            imageView.setImageResource(R.drawable.ic_fire);
        } else {
            imageView.setImageResource(R.drawable.ic_redcircle);
        }
        imageView = floatView.findViewById(R.id.ghostedEmojiTwo);
        if(Common.ghostedness==2){
            imageView.setImageResource(R.drawable.ic_fire);
        } else {
            imageView.setImageResource(R.drawable.ic_yellowcircle);
        }
        imageView = floatView.findViewById(R.id.ghostedEmojiThree);
        if(Common.ghostedness==3){
            imageView.setImageResource(R.drawable.ic_fire);
        } else {
            imageView.setImageResource(R.drawable.ic_yellowcircle);
        }
        imageView = floatView.findViewById(R.id.ghostedEmojiFour);
        if(Common.ghostedness==4){
            imageView.setImageResource(R.drawable.ic_fire);
        } else {
            imageView.setImageResource(R.drawable.ic_greencircle);
        }
        imageView = floatView.findViewById(R.id.ghostedEmojiMax);
        imageView.setImageResource(R.drawable.ic_coolglasses);
    }

    // It is called when stopService()
    // method is called in MainActivity
    @Override
    public void onDestroy() {
        super.onDestroy();
        stopSelf();
        Common.floatingRunning = false;
        // Window is removed from the screen
        windowManager.removeView(floatView);
    }
}
