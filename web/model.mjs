export function profile(cells, route, day, month) {
  const hours = Array.from({length:24}, (_, hour) => ({hour, total:0, days:0, mean:null}));
  for (const [id, period, weekday, hour, boardings, observed] of cells) {
    if (id !== route || (month !== "all" && month !== period)) continue;
    if (day === "work" && weekday > 4 || day === "weekend" && weekday < 5) continue;
    if (!["all","work","weekend"].includes(day) && weekday !== Number(day)) continue;
    hours[hour].total += boardings;
    hours[hour].days += observed;
  }
  for (const row of hours) if (row.days) row.mean = row.total / row.days;
  return hours;
}
