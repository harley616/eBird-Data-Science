import './App.css';
import React, { useState, useEffect } from 'react';
import cors from 'cors';

function App() {
  const [failed, setFailed] = useState(false);
  const [birds, setBirds] = useState(null);
  const [selectedBirds, setSelectedBirds] = useState({});
  const [topCounties, setTopCounties] = useState([]); // [county, county, county
  const url = 'http://127.0.0.1:5000';
  useEffect(() => {
    const fetchData = async () => {
      fetch(url + '/birds', {mode: 'cors' }).then(
        response => response.json()
      ).then(data => {
        setBirds(data);
      }).catch(error => {
        setFailed(true);
        console.log('There was an error getting birds', error);
      });
    }

    fetchData();
  }, [url]);

  function getCounty() {
    fetch(url + '/birds', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      }
      ,
      body: JSON.stringify(selectedBirds),
      mode: 'cors'
    }).then(response => response.json())
    .then(data => {
      console.log(data);
      setTopCounties(data);
    }).catch(error => {
      console.log('There was an error getting best countries', error);});
  }
  
  const handleSearch = (bird) => {
    const newbirds = birds;
    const hammingDistance = (str1, str2) => {
      if (str1.length !== str2.length) {
        (str1.length < str2.length) ?// normalize length
          str1 += ' '.repeat(str2.length - str1.length) :
          str2 += ' '.repeat(str1.length - str2.length);
      }
      let distance = 0;
      for (let i = 0; i < str1.length; i += 1) { // get hamming distance
        if (str1[i] !== str2[i]) {
          if (str1[i] === ' ' || str2[i] === ' ') continue; // ignore spaces
          distance += 1;
        }
      }
      return distance;
    };
    // dont look at this part ;) (sorting by hamming distance)
    const distances = newbirds.map((b) => hammingDistance(b, bird));
    const zipped = newbirds.map((b, i) => [b, distances[i]]);
    zipped.sort((a, b) => a[1] - b[1]);
    const unzipped = zipped.map((z) => z[0]);
    setBirds(unzipped);
  };

  return (
    <div className='h-screen bg-amber-100'>
        {failed && <p className='text-red-400 br'>Fetch Failed, Refresh</p>}
        <div className='h-1/2 w-full bg-amber-100'>
          <div className='font-bold text-2xl p-10 w-max mx-auto'>County Recommendation for Birding</div>

          <div className='flex h-full w-full justify-evenly pt-2'>
            <div className='h-full'>
              <div className='bg-white p-2 shadow-md rounded-sm'>Select favorite birds</div>
              <input type='text' placeholder='Search' className='p-2 rounded-sm shadow-md w-full my-1' onChange={(e) => handleSearch(e.target.value)}></input>
              <div className='h-1/2 overflow-scroll shadow-md'>
                {birds ? birds.map((bird, index) => {
                  return <div className='bg-blue-200 flex justify-between px-2 py-1' key={index}>
                    {bird} <div onClick = {() => {setSelectedBirds({...selectedBirds, [bird]: 0})}}
                    className={`border-2 ${bird in selectedBirds ? 'bg-blue-500' : 'bg-white'} h-4 w-4`}>
                      </div>
                      </div>
                }) : <p>loading...</p> }
              </div>
            </div>

            <div className='h-full'>
              <div className='bg-white p-2 mb-1 shadow-md rounded-sm'>Give bird a number rating, or click red box to remove</div>
              <div className='overflow-scroll apearance-none shadow-md'>
                {Object.keys(selectedBirds).map((bird, index) => {
                  return <div className='bg-blue-200 grid grid-cols-3  px-2 py-1' key={index}>
                    {bird} <input 
                      type='number' value={selectedBirds[bird]} 
                      onChange= {(e) => setSelectedBirds({...selectedBirds, [bird]: e.target.value})}
                      className='w-8 mx-auto'></input><div onClick = {() => {delete selectedBirds[bird]; setSelectedBirds({...selectedBirds})}}
                    className='border-2 bg-red-500 h-4 w-4 ml-auto'>
                      </div>
                    </div>
                })}
                </div>
            </div>
            <div className=''>
              <button className='bg-blue-600 hover:bg-blue-400 p-2 shadow-md rounded-sm' onClick = {() => getCounty()}>Get best County</button>
              {topCounties.map((county, index) => {
                return <div key={index}>
                  {index + 1}: {county}
                </div>
              })}
            </div>
            

          </div>
        </div>
        <div className='text-grey-400 fixed bottom-0 left-0 right-0 mx-auto w-max'>Data from: eBird Basic Dataset. Version: EBD_relMar-2024. Cornell Lab of Ornithology, Ithaca, New York. Mar 2024.</div>
    </div>
  );
}

export default App;
