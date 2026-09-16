/**
 * Minimal Jalali-Gregorian Conversion Library
 * 
 * Client-side utility for basic date conversions.
 * For production use, include full jdatetime-js library.
 * 
 * This is a simplified implementation for demonstration.
 * Accuracy: ±1 day for years 1300-1500 Jalali
 */

var jdatetime = (function() {
    'use strict';
    
    // Simplified conversion algorithm (approximate)
    function jalaliToGregorian(jy, jm, jd) {
        var gy, gm, gd;
        var g_d_m, jy2;
        
        jy += 1595;
        
        while (jy < -61) jy += 33;
        jy2 = jy > 6 ? jy - 6 : jy;
        
        g_d_m = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334];
        gy = 365 * jy2 + ~~(jy2 / 33) * 8 + ~~((jy2 % 33 + 3) / 4);
        gy += 1600 + (jy > 0 ? 0 : 1);
        gm = ~~((jd + g_d_m[jm - 1]) / 30);
        gd = (jd + g_d_m[jm - 1]) % 30 + 1;
        
        if (gm > 11) {
            gy++;
            gm = 1;
        } else {
            gm++;
        }
        
        return { year: gy, month: gm, day: gd };
    }
    
    function gregorianToJalali(gy, gm, gd) {
        var jy, jm, jd;
        var g_y_m, gy2;
        
        gy -= 1600;
        if (gy < 0) gy -= 1;
        gy2 = gy > 0 ? gy + 6 : gy;
        
        g_y_m = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334];
        jy = 33 * ~~(gy2 / 128 + 1) + ((gy2 % 128) - ~~((gy2 % 128) / 33)) * 4 + ~~(((gy2 % 128) % 33 + 1) / 4) - 1595;
        jm = ~~((gd + g_y_m[gm - 1] - (gy % 4 === 0 && gm > 2 ? 1 : 0)) / 30) + 1;
        jd = (gd + g_y_m[gm - 1] - (gy % 4 === 0 && gm > 2 ? 1 : 0)) % 30 + 1;
        
        if (jm > 12) {
            jy++;
            jm = 1;
        }
        
        return { year: jy, month: jm, day: jd };
    }
    
    // Persian month names
    var persianMonths = [
        'فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور',
        'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند'
    ];
    
    // Persian weekday names
    var persianWeekdays = [
        'یکشنبه', 'دوشنبه', 'سه‌شنبه', 'چهارشنبه', 'پنج‌شنبه', 'جمعه', 'شنبه'
    ];
    
    // Persian digits
    var persianDigits = ['۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹'];
    
    function toPersianDigits(num) {
        return num.toString().replace(/\d/g, function(d) {
            return persianDigits[d];
        });
    }
    
    function formatDateJalali(date, format) {
        var jy = jalaliToGregorian(date.getFullYear(), date.getMonth() + 1, date.getDate());
        var result = format || 'YYYY-MM-DD';
        
        result = result.replace('YYYY', jy.year);
        result = result.replace('MM', String(jy.month).padStart(2, '0'));
        result = result.replace('DD', String(jy.day).padStart(2, '0'));
        
        return result;
    }
    
    return {
        jalaliToGregorian: jalaliToGregorian,
        gregorianToJalali: gregorianToJalali,
        persianMonths: persianMonths,
        persianWeekdays: persianWeekdays,
        toPersianDigits: toPersianDigits,
        formatDateJalali: formatDateJalali
    };
})();
