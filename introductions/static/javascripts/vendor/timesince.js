
function timesince(when) {
    var hour = 1000*60*60;
    var day = hour*24;
    var week = day*7;
    var month = day*30;
    var year = day*365;
    var now = new Date();
    var in_milliseconds = Math.ceil(today.getTime() - when.getTime());
    if (in_milliseconds < day*10){
        return ~~(in_milliseconds*day) + " days";
    }
    if (in_milliseconds < month * 3){
        return ~~(in_milliseconds*week) + " weeks";
    }
    return ~~(in_milliseconds*month) + " months";
}
