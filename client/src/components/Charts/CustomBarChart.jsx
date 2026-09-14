import React from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";

const CustomBarChart = ({ data = [] }) => {
  // Generate alternate bar colors
  const getBarColor = (index) => {
    return index % 2 === 0 ? "#875cf5" : "#bfa7fc";
  };

  // Generate a suitable Y-axis maximum
  const getYAxisMax = (max) => {
    if (max <= 0) {
      return 100;
    }

    // We want approximately 5 intervals on the Y-axis
    const targetTicks = 5;

    // Estimate the size of each interval
    const roughStep = max / targetTicks;

    // Get the magnitude of the number
    const magnitude =
      10 ** Math.floor(Math.log10(roughStep));

    // Normalize the step
    const normalized = roughStep / magnitude;

    // Choose a nice step size
    let niceStep;

    if (normalized <= 1) {
      niceStep = 1;
    } else if (normalized <= 2) {
      niceStep = 2;
    } else if (normalized <= 5) {
      niceStep = 5;
    } else {
      niceStep = 10;
    }

    niceStep *= magnitude;

    // Round the maximum up to the nearest nice step
    return Math.ceil(max / niceStep) * niceStep;
  };

  // Find the largest amount
  const maxAmount = Math.max(
    ...data.map((item) => Number(item.amount) || 0),
    0
  );

  // Calculate Y-axis maximum
  const yAxisMax = getYAxisMax(maxAmount);

  // Custom tooltip
  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white shadow-md rounded-lg p-2 border border-gray-300">
          <div className="text-sm text-gray-600 flex gap-1">
            <span className="text-[#875cf5]">
              Amount:
            </span>

            <span className="text-sm font-medium text-gray-900">
              ₹{Number(payload[0].payload.amount).toLocaleString("en-IN")}
            </span>
          </div>
        </div>
      );
    }

    return null;
  };

  return (
    <div className="bg-white mt-6">
      <ResponsiveContainer width="100%" height={550}>
        <BarChart
          data={data}
          margin={{
            top: 20,
            right: 20,
            left: 10,
            bottom: 10,
          }}
        >
          <XAxis
            dataKey="date"
            tick={{
              fontSize: 12,
              fill: "#555",
              stroke: "none",
            }}
          />

          <YAxis
            domain={[0, yAxisMax]}
            tick={{
              fontSize: 12,
              fill: "#555",
              stroke: "none",
            }}
          />

          <Tooltip
            content={<CustomTooltip />}
            cursor={false}
          />

          <Bar
            dataKey="amount"
            radius={[10, 10, 0, 0]}
            maxBarSize={70}
          >
            {data.map((entry, index) => (
              <Cell
                key={index}
                fill={getBarColor(index)}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default CustomBarChart;