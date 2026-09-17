/** @odoo-module **/

import { Component, useState, onMounted, onWillUnmount } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";

/**
 * Jalali Status Bar Component - Production Ready
 * 
 * Displays current Jalali date in the status bar.
 * Updates automatically and shows Persian date alongside Gregorian.
 * Properly cleans up interval on component unmount to prevent memory leaks.
 */
export class JalaliStatus extends Component {
    static template = "zarvan_calendar.JalaliStatus";
    
    setup() {
        this.orm = useService("orm");
        this.state = useState({
            jalaliDate: '',
            jalaliWeekday: '',
            isLoading: true,
        });
        
        let intervalId = null;
        
        onMounted(async () => {
            await this.updateDate();
            // Update every minute
            intervalId = setInterval(() => this.updateDate(), 60000);
        });
        
        // Clean up interval on component unmount to prevent memory leaks
        onWillUnmount(() => {
            if (intervalId) {
                clearInterval(intervalId);
                intervalId = null;
            }
        });
    }
    
    async updateDate() {
        try {
            const today = new Date();
            const result = await this.orm.call('jalaali.mixin', 'gregorian_to_jalali', [
                today.getFullYear(),
                today.getMonth() + 1,
                today.getDate(),
            ]);
            
            if (result) {
                const weekdays = ['یکشنبه', 'دوشنبه', 'سه‌شنبه', 'چهارشنبه', 'پنج‌شنبه', 'جمعه', 'شنبه'];
                const weekday = weekdays[today.getDay()];
                
                this.state.jalaliWeekday = weekday;
                this.state.jalaliDate = `${result[0]}/${String(result[1]).padStart(2, '0')}/${String(result[2]).padStart(2, '0')}`;
                this.state.isLoading = false;
            }
        } catch (error) {
            console.error('Error loading Jalali date:', error);
            this.state.isLoading = false;
        }
    }
}

// Register component in appropriate category
registry.category("components").add("JalaliStatus", JalaliStatus);
