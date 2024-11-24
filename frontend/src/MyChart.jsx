import { Chart as ChartJS, defaults } from "chart.js/auto";
import { Bar, Doughnut, Line} from "react-chartjs-2";

defaults.responsive = true;

export const MyChart = () => {
    return (
        <div>
            <Bar
                data={{
                    labels: ["A", "B", "C"],
                    datasets: [
                        {
                            label: "Revenue",
                            data: [200, 300, 400]
                        }
                    ]
                }
                }
            ></Bar>
        </div>
    )
}

export default MyChart;