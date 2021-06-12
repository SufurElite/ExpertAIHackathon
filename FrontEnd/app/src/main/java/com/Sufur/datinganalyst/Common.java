package com.Sufur.datinganalyst;

import android.graphics.Bitmap;

import com.google.firebase.auth.FirebaseUser;

public class Common {
    // the string will be saved in here when min/max is pressed
    public static String currentDesc = "";
    // string stored here when save is pressed
    public static String savedDesc = "";
    public static FirebaseUser currentUser;
    public static Bitmap bitmap;
    public static boolean analysis = false;
    public static int displayWidth;
    public static int displayHeight;

}
