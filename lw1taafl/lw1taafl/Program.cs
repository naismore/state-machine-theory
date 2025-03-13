using CsvHelper;
using CsvHelper.Configuration;
using System.Globalization;
namespace lw1taafl
{
    public class MealyState
    { 
        public string? CurrentState { get; set; }
        public string? NextState { get; set; }
        public string? Output { get; set; }
        public string? Input { get; set; }
    }

    public class MooreState
    { 
        public string? NextState { get; set; }
        public string? Output { get; set; }
        public string? Input { get; set; }
        public string? NameState { get; set; }
    }
    
    internal class Program
    {
        static void Main(string[] args)
        {
            string path = "input2.csv";
            List<MooreState> mooreStates = ReadMooreCsv(path);
            List<MealyState> mealyStates = new();
            List<string> inputSignals = new();
            foreach (var state in mooreStates)
            {
                Console.WriteLine($"Name: {state.NameState}, Input: {state.Input}, Next State: {state.NextState}, Output: {state.Output}");
            }
            foreach (var state in mooreStates)
            {
                if (!inputSignals.Contains(state.Input!))
                {
                    inputSignals.Add(state.Input!);
                }
                mealyStates.Add(new MealyState
                {
                    CurrentState = state.NameState,
                    NextState = state.NextState,
                    Output = state.Output,
                    Input = state.Input
                });
            }

            foreach (var transition in mealyStates)
            {
                Console.WriteLine($"Current State: {transition.CurrentState}, Input: {transition.Input}, Next State: {transition.NextState}, Output: {transition.Output}");
            }

            Console.Write(";");
            foreach (var state in mealyStates)
            {
                Console.Write($"{state.CurrentState};");
            }
            Console.WriteLine();
            int inputSignalsCount = 0;
            Console.Write($"{inputSignals[inputSignalsCount]};");
            for (int i = 0; i < inputSignals.Count; i++)
            {
                foreach (var state in mealyStates)
                {
                    if (state.Input == inputSignals[inputSignalsCount])
                        Console.Write($"{state.NextState}/{state.Output};");
                }
                Console.WriteLine();
                inputSignalsCount++;
                if (inputSignalsCount >= inputSignals.Count)
                {
                    break;
                }
                Console.Write($"{inputSignals[inputSignalsCount]};");
            }
        }

        static void MealyToMoore()
        {
            List<MooreState> mooreStates = new();
            List<string> inputSignals = new();
            string path = "input1.csv";
            List<MealyState> mealyStates = ReadMealy(path);
            var transitions = ReadMealy(path);
            foreach (var transition in transitions)
            {
                Console.WriteLine($"Current State: {transition.CurrentState}, Input: {transition.Input}, Next State: {transition.NextState}, Output: {transition.Output}");
            }
            int index = 0;
            foreach (var transition in transitions)
            {
                if (!inputSignals.Contains(transition.Input!))
                {
                    inputSignals.Add(transition.Input!);
                }
                var tempState = new MooreState
                {
                    NextState = transition.NextState!,
                    Output = transition.Output!,
                    Input = transition.Input!,
                    NameState = $"q{index}"
                };
                if (!ExistState(mooreStates, tempState))
                {
                    mooreStates.Add(new MooreState
                    {
                        NextState = transition.NextState!,
                        Output = transition.Output!,
                        Input = transition.Input!,
                        NameState = $"q{index}"
                    });
                    index++;
                }

            }
            Console.WriteLine();
            foreach (var state in mooreStates)
            {
                Console.WriteLine($"Name: {state.NameState}, Input: {state.Input}, Next State: {state.NextState}, Output: {state.Output}");
            }
            Console.WriteLine("Hello, World!");

            Console.Write(";");
            foreach (var state in mooreStates)
            {
                Console.Write($"{state.Output};");
            }
            Console.WriteLine();
            Console.Write(";");
            foreach (var state in mooreStates)
            {
                Console.Write($"{state.NameState};");
            }
            Console.WriteLine();
            int inputSignalsCount = 0;
            Console.Write($"{inputSignals[inputSignalsCount]};");
            for (int i = 0; i < inputSignals.Count; i++)
            {
                foreach (var state in mooreStates)
                {
                    foreach (var tempState in transitions)
                    {
                        if (state.NextState == tempState.CurrentState &&
                            tempState.Input == inputSignals[inputSignalsCount])
                        {
                            Console.Write($"{GetMooreStateName(mooreStates, tempState)};");
                        }
                    }
                }
                Console.WriteLine();
                inputSignalsCount++;
                if (inputSignalsCount >= inputSignals.Count)
                {
                    break;
                }
                Console.Write($"{inputSignals[inputSignalsCount]};");
            }
        }

        static string? GetMooreStateName(List<MooreState> mooreStates, MealyState state)
        {
            foreach (var mooreState in mooreStates)
            {
                if (state.NextState == mooreState.NextState &&
                    state.Output == mooreState.Output)
                    return mooreState.NameState!;
            }
            return null;
        }

        static bool ExistState(List<MooreState> mooreStates, MooreState state)
        {
            foreach (var mooreState in mooreStates)
            {
                if (mooreState.NextState == state.NextState && mooreState.Output == state.Output)
                { return true; }
            }
            return false;
        }

        static List<MealyState> ReadMealy(string filePath)
        {
            var transitions = new List<MealyState>();
            var config = new CsvConfiguration(CultureInfo.InvariantCulture)
            {
                Delimiter = ";",
                HeaderValidated = null,
                MissingFieldFound = null
            };
            using (var reader = new StreamReader(filePath))
            using (var csv = new CsvReader(reader, config))
            {
                csv.Read();
                csv.ReadHeader();
                var outputChars = csv.HeaderRecord![1..];

                while (csv.Read())
                {
                    var inputChar = csv.GetField(0);
                    for (int i = 0; i < outputChars.Length + 1; i++)
                    {
                        var transition = csv.GetField(i);
                        var parts = transition!.Split('/');
                        if (parts.Length == 2)
                        {
                            var nextState = parts[0];
                            var outputChar = parts[1];
                            var currentState = outputChars[i - 1];

                            transitions.Add(new MealyState
                            {
                                CurrentState = currentState,
                                NextState = nextState,
                                Input = inputChar,
                                Output = outputChar
                            });
                        }
                    }
                }
            }
            return transitions;
        }

        static List<MooreState> ReadMooreCsv(string filePath)
        {
            var config = new CsvConfiguration(CultureInfo.InvariantCulture)
            {
                Delimiter = ";", // Укажите разделитель
                HeaderValidated = null, // Игнорировать проверку заголовков
                MissingFieldFound = null // Игнорировать отсутствующие поля
            };

            var mooreStates = new List<MooreState>();

            using (var reader = new StreamReader(filePath))
            using (var csv = new CsvReader(reader, config))
            {
                // Чтение заголовков (выходные символы)
                csv.Read();
                csv.ReadHeader();
                var outputSymbols = csv.HeaderRecord![1..]; // Получаем выходные символы

                // Чтение состояний
                csv.Read(); // Читаем строку с состояниями
                var states = new List<string>(); // Получаем состояния
                for (int i = 0; i < outputSymbols.Length; i++)
                {
                    states.Add(csv.GetField(i));
                }

                // Чтение переходов
                while (csv.Read())
                {
                    var inputSymbol = csv.GetField(0); // Получаем входной символ
                    for (int i = 1; i < states.Count + 1; i++) // Проходим по всем состояниям
                    {
                        var nextState = csv.GetField(i); // Получаем следующее состояние
                        var outputSymbol = outputSymbols[i - 1]; // Получаем выходной символ

                        mooreStates.Add(new MooreState
                        {
                            Input = inputSymbol, // Входной символ
                            NextState = nextState, // Следующее состояние
                            Output = outputSymbol, // Выходной символ
                            NameState = $"q{i - 1}" // Имя состояния
                        });
                    }
                }
            }

            return mooreStates;
        }
    }
}

