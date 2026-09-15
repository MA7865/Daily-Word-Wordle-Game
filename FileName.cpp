#include <iostream>
#include <string>
#include <fstream>
#include <vector>
#include<random>
#include<ctime>
#include <map>
using namespace std;

void get5LetterWords(const string& filename, const string& fileout);
vector<string> loadWords(const string& filename);
string get_random_word(const vector<string>& words);
bool check_if_5_letters(const string& user_input);
bool check_if_in_dictionary(const string& user_input, const vector<string>& words);
string performWordle(const string& answer, const string& user_input);
void playWordle(const vector<string>& words);
void menu();


int main(int argc, char* argv[])
{
    //get5LetterWords("words_alpha.txt", "words5.txt");
    /*menu();
    vector<string> words = loadWords("words5.txt");
    playWordle(words);*/


    vector<string> words = loadWords("words5.txt");

    // Handle command line arguments for Python interface
    if (argc > 1) {
        string option = argv[1];

        if (option == "--get-word") {
            // Just output a random word
            cout << get_random_word(words);
            return 0;
        }
        else if (option == "--check-guess" && argc == 4) {
            // Check a guess against an answer
            string answer = argv[2];
            string guess = argv[3];

            if (!check_if_5_letters(guess) || !check_if_in_dictionary(guess, words)) {
                cerr << "Invalid guess";
                return 1;
            }

            cout << performWordle(answer, guess);
            return 0;
        }
    }

    // Normal game mode
    menu();
    playWordle(words);

    return 0;
}

void get5LetterWords(const string& filename, const string& fileout) //&: to avoid sending whole copy of file eventhough we aren't chnaging anything in it (constant string ensures this_. usese less memory and is more efficient
{
    ifstream fin(filename); //opening file to read
    ofstream fout(fileout); //opening file to write

    if (!fin.is_open() || !fout.is_open()) //exception handling
    {
        cerr << "Error opening files!" << endl;
        return;
    }

    string line;
    while (getline(fin, line)) {
        if (line.length() == 5) { //checking length of letters
            fout << line << '\n'; //writing it in output file
        }
    }
    fin.close();
    fout.close();
}

vector<string> loadWords(const string& filename) {
    vector<string> words; //empty vector string to store words from words5.txt file

    ifstream fin(filename); //open the input file

    if (!fin.is_open()) {  //exception handling
        cerr << "Error opening file!" << endl;
        return words;
    }
    string word;
    while (getline(fin, word)) {
        words.push_back(word);
    }
    fin.close();
    return words;
}

string get_random_word(const vector<string>& words) {
    srand(time(0));
    int r = rand() % words.size(); //generating random index 
    return words[r]; //returning the word at that random index
}

bool check_if_5_letters(const string& user_input) { //&-->efficiency and const --->so that argument not chnaged
    if (user_input.length() != 5)
        return false;
    for (char c : user_input) // each characher of string user_input will be assigned to c - just to check if they r all alphabetic
        if (!isalpha(c))
            return false;
    return true;
}

bool check_if_in_dictionary(const string& user_input, const vector<string>& words) {
    for (const string& word : words)
    {
        if (word == user_input)  // to check if input matches a word in the vector
            return true;
    }
    return false;
}

//menu for users to know how the game works
void menu()
{
    cout << "=====================\n";
    cout << "     WORDLE GAME     \n";
    cout << "=====================\n";
    cout << "Rules:\n";
    cout << "- Guess the 5-letter word in 6 tries.\n";
    cout << "- After each guess:\n";
    cout << "  * Green letter: correct letter in the correct spot.\n";
    cout << "  * Yellow letter: letter is in the word but wrong spot.\n";
    cout << "  * Grey letter: letter is not in the word.\n";
    cout << "Good luck!\n\n";
}


//returns feedback: green +,yellow *, grey -
string performWordle(const string& answer, const string& user_input)
{
    // If the guess is completely correct, turn everything green directly
    if (user_input == answer)
    {
        string all_green = "";
        for (char c : user_input)
        {
            all_green += "\033[32m" + string(1, c) + "\033[0m";  // green color
        }
        return all_green;
    }

    map<char, int> letter_count;
    for (char c : answer)
        letter_count[c]++;

    string result = user_input;  // Start with the user's input
    vector<char> feedback(5, '-');  // To track correctness

    // First pass: correct position (green)
    for (int i = 0; i < 5; i++)
    {
        if (user_input[i] == answer[i])
        {
            feedback[i] = '+';
            letter_count[user_input[i]]--;
        }
    }

    // Second pass: correct letter but wrong position (yellow)
    for (int i = 0; i < 5; i++)
    {
        if (feedback[i] == '-' && letter_count[user_input[i]] > 0)
        {
            feedback[i] = '*';
            letter_count[user_input[i]]--;
        }
    }

    // Now color the word
    string colored_word = "";
    for (int i = 0; i < 5; i++)
    {
        if (feedback[i] == '+')
            colored_word += "\033[32m" + string(1, user_input[i]) + "\033[0m";  // green
        else if (feedback[i] == '*')
            colored_word += "\033[33m" + string(1, user_input[i]) + "\033[0m";  // yellow
        else
            colored_word += "\033[90m" + string(1, user_input[i]) + "\033[0m";  // grey
    }

    return colored_word;
}

// Main game loop
void playWordle(const vector<string>& words)
{
    bool playAgain;

    while (true)
    {
        int attempts = 0;
        string answer = get_random_word(words);  // Select a random word from the list
        cout << "(Debug) Randomly selected word: " << answer << '\n';  // (Optional, remove later)

        while (true)
        {
            if (attempts < 6)
            {
                string user_input;
                cout << "Enter your guess: ";
                getline(cin, user_input);

                bool valid_length = check_if_5_letters(user_input);
                bool exists_in_dict = check_if_in_dictionary(user_input, words);

                if (valid_length == false)
                {
                    cout << "Invalid input! Please enter exactly 5 alphabetic letters.\n";
                    continue;
                }
                if (exists_in_dict == false)
                {
                    cout << "Word not found in dictionary. Try again.\n";
                    continue;
                }

                attempts++;

                string result = performWordle(answer, user_input);
                cout << result << '\n';

                if (user_input == answer)
                {
                    cout << "Congratulations! You guessed it in " << attempts << " attempt(s)!\n\n";
                    break;
                }
            }
            else
            {
                cout << "You ran out of attempts!\n\n";
                break;
            }
        }
        cout << "Would you like to play again? (Yes = 1, No = 0): ";
        cin >> playAgain;
        cin.ignore();
        cout << endl;

        if (playAgain == 0)
        {
            cout << "Shutting down..\n";
            break;
        }
    }
}