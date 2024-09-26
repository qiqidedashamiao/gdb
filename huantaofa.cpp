#include <iostream>
#include <vector>
#include <algorithm>
#include <fstream>
#include <string>
#include <ctime>
#include <time.h>
#include <chrono>
using namespace std;
vector<int> f;
int minf = -1;
int n;
vector<int> flag;
void digui(vector<vector<int> > &heights, int index, int height, vector<int> path)
{
    if (height >= minf)
    {
        return ;
    }
    if (index == 0)
    {
        if (height < minf)
        {
            f = path;
            minf = height;
        }
        return ;
    }
    for (int i = index-1; i >= 0; --i)
    {
        if (heights[i][1] <= heights[index][1] && flag[i])
        {
            path.push_back(i);
            int temp = heights[i][0] - heights[index][0] - height/2;
            if (temp < 0)
            {
                temp = 0;
            }
            if (i == 0)
            {
                digui(heights, i, height + temp, path);
            }
            else 
            {
                digui(heights, i, height + temp + temp%2, path);
            }
            path.pop_back();
        }
    }

}
int main()
{
    // int n;
    cin >> n;
    
    vector<vector<int> > heights(n+1, vector<int>(2));
    f.resize(n+1);
    flag.resize(n+1);
    for (int i = 0; i < n; i++)
    {
        cin >> heights[i][0] >> heights[i][1];
        if (heights[i][1] >= heights[0][1])
        {
            flag[i] = 1;
        }
    }
    heights[n][0] = 0;
    heights[n][1] = 9999999;
    flag[n] = 1;
    minf = heights[0][0];
    vector<int> path;
    digui(heights, n, 0, path);
    cout << minf << endl;

    return 0;
}